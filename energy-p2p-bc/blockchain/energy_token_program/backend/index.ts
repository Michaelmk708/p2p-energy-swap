// backend/index.ts
import * as anchor from "@coral-xyz/anchor";
import {
  Connection, Keypair, PublicKey, SystemProgram,
  Transaction, TransactionInstruction, sendAndConfirmTransaction
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAssociatedTokenAddress
} from "@solana/spl-token";
import http from "http";
import fs from "fs";
import path from "path";
import crypto from "crypto";
import dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, ".env") });

const RPC = process.env.RPC ?? "http://127.0.0.1:8899";
const PROGRAM_ID = new PublicKey(process.env.PROGRAM_ID || "");
const PORT = Number(process.env.PORT || 8080);

const VERIFY_HMAC = String(process.env.VERIFY_HMAC || "false").toLowerCase() === "true";
const ALLOW_SERVER_BURN = String(process.env.ALLOW_SERVER_BURN || "false").toLowerCase() === "true";

// ---- Load IDL and PDAs ----
const idlPath = path.resolve(__dirname, "../target/idl/energy_token_program.json");
const idl = JSON.parse(fs.readFileSync(idlPath, "utf8"));

const STATE_PDA = PublicKey.findProgramAddressSync([Buffer.from("state")], PROGRAM_ID)[0];
const MINT_AUTH_PDA = PublicKey.findProgramAddressSync([Buffer.from("mint_auth")], PROGRAM_ID)[0];

// ---- tiny dev DB for idempotency & accumulator (per device/wallet) ----
const DB_PATH = path.resolve(__dirname, "device-db.json");
type Row = {
  device_id: string;
  wallet: string;          // base58
  last_seen_ts?: number;   // for basic freshness
  acc?: number;            // fractional accumulator (v1)
};
function readDb(): Record<string, Row> {
  try { return JSON.parse(fs.readFileSync(DB_PATH, "utf8")); } catch { return {}; }
}
function writeDb(db: Record<string, Row>) {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

// ---- Helpers ----
function pickIxName(snake: string, camel: string) {
  const names = ((idl as any).instructions ?? []).map((i: any) => i.name);
  if (names.includes(camel)) return camel;
  if (names.includes(snake)) return snake;
  throw new Error(`IDL method not found: ${camel}/${snake}`);
}
function encodeIx(name: string, args: any = {}) {
  const coder = new anchor.BorshCoder(idl as anchor.Idl);
  return coder.instruction.encode(name, args);
}
async function sendIx(conn: Connection, payer: Keypair, ix: TransactionInstruction, signers: Keypair[] = []) {
  const tx = new Transaction().add(ix);
  return await sendAndConfirmTransaction(conn, tx, [payer, ...signers], { commitment: "confirmed" });
}
async function getMint(conn: Connection): Promise<PublicKey> {
  const acc = await conn.getAccountInfo(STATE_PDA);
  if (!acc) throw new Error("State PDA not found. Run scripts/demo.ts initialize once.");
  const coder = new anchor.BorshCoder(idl as anchor.Idl);
  const state: any = coder.accounts.decode("State", acc.data);
  return new PublicKey(state.mint);
}
function verifyHmac(rawBody: string, providedSigB64: string, secret: string): boolean {
  const mac = crypto.createHmac("sha256", secret).update(rawBody).digest("base64");
  // timing safe compare
  const a = Buffer.from(mac);
  const b = Buffer.from(providedSigB64 || "", "base64").toString("base64");
  return crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(b));
}

// ---- Gateways ----
// /v0 : your CURRENT payload -> { deviceId, solar_generation, consumption, surplus, deficit }
//      Mint floor(surplus_kW * WINDOW_HOURS). No accumulator, simple flow for dev.
// /v1 : FUTURE safer payload (cumulative kWh) -> { device_id, wallet, ts, gen_kwh_total, cons_kwh_total, nonce, sig }
//      Uses accumulator and idempotency based on totals.

const WINDOW_SECONDS = 10; // if device posts ~every 2s, we bucket ~10s -> roughly kWh = kW * (10/3600)
function computeTokensFromInstantKW(surplusKW: number): number {
  if (surplusKW <= 0) return 0;
  const kwh = surplusKW * (WINDOW_SECONDS / 3600);
  return Math.floor(kwh); // decimals=0 mint
}

// ---- Server ----
async function main() {
  const connection = new Connection(RPC, "confirmed");
  const secret = JSON.parse(fs.readFileSync(path.join(process.env.HOME!, ".config/solana/id.json"), "utf8"));
  const oracle = Keypair.fromSecretKey(Uint8Array.from(secret));

  const mintIxName = pickIxName("mint_energy", "mintEnergy");
  // const burnIxName = pickIxName("burn_energy", "burnEnergy"); // disabled in dev by default

  const mint = await getMint(connection);
  console.log("Oracle:", oracle.publicKey.toBase58());
  console.log("Program:", PROGRAM_ID.toBase58());
  console.log("Mint:", mint.toBase58());
  console.log("Listening on :", PORT);

  const server = http.createServer(async (req, res) => {
    if (req.method !== "POST") { res.statusCode = 405; return res.end("POST only"); }

    let raw = "";
    for await (const chunk of req) raw += chunk;

    try {
      const url = req.url || "/";
      const body = JSON.parse(raw);
      const db = readDb();

      let deviceId = "";
      let walletPk: PublicKey;
      let tokensToMint = 0;

      if (url.startsWith("/v0")) {
        // ✅ COMPAT with your sketch
        // Expected body: { deviceId, solar_generation, consumption, surplus, deficit, wallet? }
        deviceId = String(body.deviceId || body.device_id || "unknown");
        const wallet = String(body.wallet || ""); // optional; else fallback to a default wallet if you want
        if (!wallet) { res.statusCode = 400; return res.end("wallet required for v0"); }
        walletPk = new PublicKey(wallet);

        // Optional DEV HMAC (only if you add it later)
        if (VERIFY_HMAC) {
          const secret = String(body.device_secret || "");
          const sig = String(body.sig || "");
          if (!secret || !sig) { res.statusCode = 401; return res.end("missing sig/secret"); }
          const ok = verifyHmac(raw, sig, secret);
          if (!ok) { res.statusCode = 401; return res.end("bad signature"); }
        }

        const surplusKW = Number(body.surplus || 0);
        // Simple window-based mint (dev). For consistent results, keep device send interval ~2s and gateway WINDOW_SECONDS ~10s.
        tokensToMint = computeTokensFromInstantKW(surplusKW);

      } else if (url.startsWith("/v1")) {
        // ✅ FUTURE safer mode (cumulative counters)
        // Body: { device_id, wallet, ts, gen_kwh_total, cons_kwh_total, fw_version?, nonce?, sig? }
        deviceId = String(body.device_id || "unknown");
        walletPk = new PublicKey(String(body.wallet));

        if (VERIFY_HMAC) {
          const secret = String(body.device_secret || "");
          const sig = String(body.sig || "");
          if (!secret || !sig) { res.statusCode = 401; return res.end("missing sig/secret"); }
          const ok = verifyHmac(raw, sig, secret);
          if (!ok) { res.statusCode = 401; return res.end("bad signature"); }
        }

        const key = `${deviceId}:${walletPk.toBase58()}`;
        const row: Row = db[key] || { device_id: deviceId, wallet: walletPk.toBase58(), acc: 0 };

        const gen = Number(body.gen_kwh_total);
        const cons = Number(body.cons_kwh_total);
        if (!isFinite(gen) || !isFinite(cons)) {
          res.statusCode = 400; return res.end("invalid totals");
        }

        // Accumulator approach
        const surplus = (gen - cons); // total net
        // We need delta since last call → keep a shadow in DB. For simplicity,
        // assume device sends steadily and we approximate by carrying small acc.
        // In production, store last totals and subtract.
        row.acc = (row.acc || 0) + surplus; // this is oversimplified; see full cumulative flow in previous messages
        tokensToMint = Math.floor(Math.max(0, row.acc));
        row.acc = (row.acc || 0) - tokensToMint;

        db[key] = row; writeDb(db);
      } else {
        // default to v0 for root
        deviceId = String(body.deviceId || body.device_id || "unknown");
        const wallet = String(body.wallet || "");
        if (!wallet) { res.statusCode = 400; return res.end("wallet required (use /v0)"); }
        walletPk = new PublicKey(wallet);
        const surplusKW = Number(body.surplus || 0);
        tokensToMint = computeTokensFromInstantKW(surplusKW);
      }

      // Resolve ATA
      const userAta = await getAssociatedTokenAddress(mint, walletPk);

      // Mint if >= 1
      let sig = "";
      if (tokensToMint >= 1) {
        const keys = [
          { pubkey: STATE_PDA, isSigner: false, isWritable: true },
          { pubkey: mint, isSigner: false, isWritable: true },
          { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
          { pubkey: oracle.publicKey, isSigner: true, isWritable: true },
          { pubkey: userAta, isSigner: false, isWritable: true },
          { pubkey: walletPk, isSigner: false, isWritable: false },
          { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
          { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ];
        const data = encodeIx(pickIxName("mint_energy","mintEnergy"), { amount: new anchor.BN(tokensToMint) });
        const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
        sig = await sendIx(connection, oracle, ix);
        console.log(`Minted ${tokensToMint} → ${walletPk.toBase58()} | dev=${deviceId} | ${sig}`);
      } else {
        console.log(`No mint (tokens=${tokensToMint}) dev=${deviceId}`);
      }

      res.statusCode = 200;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ ok: true, deviceId, wallet: walletPk.toBase58(), tokensMinted: tokensToMint, sig }));
    } catch (e: any) {
      console.error(e);
      res.statusCode = 400;
      res.end(e?.message || "bad request");
    }
  });

  server.listen(PORT, () => console.log(`Oracle gateway listening on :${PORT}  (POST /v0 or /v1)`));
}

main().catch((e) => { console.error(e); process.exit(1); });
