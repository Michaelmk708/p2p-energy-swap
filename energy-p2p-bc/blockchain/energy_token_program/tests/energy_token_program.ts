// tests/energy_token_program.ts
import * as anchor from "@coral-xyz/anchor";
import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  getAccount as getSplAccount,
  getMint,
} from "@solana/spl-token";
import { expect } from "chai";
import fs from "fs";
import path from "path";

/**
 * Test goals:
 * 1) initialize once (or detect already-initialized)
 * 2) mint by oracle increases ATA balance
 * 3) non-oracle cannot mint (negative)
 * 4) burn by user decreases balance
 * 5) burn without user signature fails (negative)
 */

const RPC = process.env.ANCHOR_PROVIDER_URL ?? "http://127.0.0.1:8899";
const PROGRAM_ID = new PublicKey("6WnjPtMbz6ogoJg2PgGnbnyEW4uEmPV6EqzLQ4BqouPo");

const idlPath = path.resolve(__dirname, "../target/idl/energy_token_program.json");
const idl = JSON.parse(fs.readFileSync(idlPath, "utf8"));

const STATE_PDA = PublicKey.findProgramAddressSync([Buffer.from("state")], PROGRAM_ID)[0];
const MINT_AUTH_PDA = PublicKey.findProgramAddressSync([Buffer.from("mint_auth")], PROGRAM_ID)[0];

// ---------- helpers ----------
function providerFromLocalKeypair() {
  const connection = new Connection(RPC, "confirmed");
  const home = process.env.HOME || process.env.USERPROFILE!;
  const secret = JSON.parse(fs.readFileSync(path.join(home, ".config/solana/id.json"), "utf8"));
  const payer = Keypair.fromSecretKey(Uint8Array.from(secret));
  const wallet = new anchor.Wallet(payer);
  const provider = new anchor.AnchorProvider(connection, wallet, { commitment: "confirmed" });
  return { connection, payer, wallet, provider };
}

function encodeIx(name: string, args: any = {}) {
  const coder = new anchor.BorshCoder(idl as anchor.Idl);
  return coder.instruction.encode(name, args);
}

function pickIxName(snake: string, camel: string) {
  const names = ((idl as any).instructions ?? []).map((i: any) => i.name);
  if (names.includes(camel)) return camel;
  if (names.includes(snake)) return snake;
  throw new Error(`Instruction not in IDL. Tried "${camel}" & "${snake}". Found: ${names.join(", ")}`);
}

async function sendTx(
  connection: Connection,
  payer: Keypair,
  ix: TransactionInstruction,
  signers: Keypair[] = []
) {
  const tx = new Transaction().add(ix);
  return await sendAndConfirmTransaction(connection, tx, [payer, ...signers], {
    commitment: "confirmed",
  });
}

async function fetchState(connection: Connection) {
  const info = await connection.getAccountInfo(STATE_PDA);
  if (!info) return null;
  const coder = new anchor.BorshCoder(idl as anchor.Idl);
  return coder.accounts.decode("State", info.data) as { mint: PublicKey; oracle: PublicKey };
}

// ---------- tests ----------
describe("energy_token_program", () => {
  const { connection, payer, wallet } = providerFromLocalKeypair();
  let mint: PublicKey;
  let user: Keypair;
  let userAta: PublicKey;

  const ixInitialize = pickIxName("initialize", "initialize");
  const ixMint = pickIxName("mint_energy", "mintEnergy");
  const ixBurn = pickIxName("burn_energy", "burnEnergy");

  before("airdrop to payer and create user", async () => {
    await connection.requestAirdrop(wallet.publicKey, 0.5 * LAMPORTS_PER_SOL);
    user = Keypair.generate();
    await connection.requestAirdrop(user.publicKey, 0.5 * LAMPORTS_PER_SOL);
  });

  it("initialize (idempotent)", async () => {
    const freshMint = Keypair.generate();

    const keys = [
      { pubkey: STATE_PDA, isSigner: false, isWritable: true },
      { pubkey: freshMint.publicKey, isSigner: true, isWritable: true },
      { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const data = encodeIx(ixInitialize, { oracle: wallet.publicKey });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });

    try {
      const sig = await sendTx(connection, payer, ix, [freshMint]);
      expect(sig).to.be.a("string");
      mint = freshMint.publicKey;
    } catch {
      const state = await fetchState(connection);
      expect(state).to.not.eq(null);
      mint = (state as any).mint as PublicKey;
    }

    // ✅ Assert real SPL mint invariants
    const accInfo = await connection.getAccountInfo(mint);
    expect(accInfo).to.not.eq(null);
    expect((accInfo as any).owner.toBase58()).to.eq(TOKEN_PROGRAM_ID.toBase58());

    const mintInfo = await getMint(connection, mint);
    expect(mintInfo.decimals).to.eq(0);
    expect(mintInfo.mintAuthority?.toBase58()).to.eq(MINT_AUTH_PDA.toBase58());
  });

  it("mint by oracle increases balance", async () => {
    userAta = await getAssociatedTokenAddress(mint, user.publicKey);
    const before = await connection.getTokenAccountBalance(userAta).catch(() => null);
    const beforeAmt = before ? Number(before.value.amount) : 0;

    const keys = [
      { pubkey: STATE_PDA, isSigner: false, isWritable: true },
      { pubkey: mint, isSigner: false, isWritable: true },
      { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true }, // oracle signer
      { pubkey: userAta, isSigner: false, isWritable: true }, // create if needed
      { pubkey: user.publicKey, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const data = encodeIx(ixMint, { amount: new anchor.BN(3) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
    await sendTx(connection, payer, ix);

    const after = await getSplAccount(connection, userAta);
    expect(Number(after.amount)).to.eq(beforeAmt + 3);
  });

  it("non-oracle cannot mint (negative)", async () => {
    const rogue = Keypair.generate();
    await connection.requestAirdrop(rogue.publicKey, 0.5 * LAMPORTS_PER_SOL);

    const keys = [
      { pubkey: STATE_PDA, isSigner: false, isWritable: true },
      { pubkey: mint, isSigner: false, isWritable: true },
      { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
      { pubkey: rogue.publicKey, isSigner: true, isWritable: true }, // WRONG oracle
      { pubkey: userAta, isSigner: false, isWritable: true },
      { pubkey: user.publicKey, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const data = encodeIx(ixMint, { amount: new anchor.BN(1) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });

    let failed = false;
    try {
      await sendTx(connection, payer, ix, [rogue]);
    } catch {
      failed = true;
    }
    expect(failed).to.eq(true);
  });

  it("burn by user decreases balance", async () => {
    const before = await getSplAccount(connection, userAta);
    const beforeAmt = Number(before.amount);

    const keys = [
      { pubkey: mint, isSigner: false, isWritable: true }, // writable for total supply update
      { pubkey: userAta, isSigner: false, isWritable: true },
      { pubkey: user.publicKey, isSigner: true, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const data = encodeIx(ixBurn, { amount: new anchor.BN(1) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
    await sendTx(connection, payer, ix, [user]);

    const after = await getSplAccount(connection, userAta);
    expect(Number(after.amount)).to.eq(beforeAmt - 1);
  });

  it("burn without user signature fails (negative)", async () => {
    const keys = [
      { pubkey: mint, isSigner: false, isWritable: true },
      { pubkey: userAta, isSigner: false, isWritable: true },
      { pubkey: user.publicKey, isSigner: true, isWritable: true }, // marked signer in metas…
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const data = encodeIx(ixBurn, { amount: new anchor.BN(1) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });

    let failed = false;
    try {
      // …but do NOT include `user` in the tx signers => should fail
      await sendTx(connection, payer, ix /* no [user] */);
    } catch {
      failed = true;
    }
    expect(failed).to.eq(true);
  });
});
