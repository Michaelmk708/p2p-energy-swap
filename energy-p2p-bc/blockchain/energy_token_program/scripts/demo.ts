// scripts/demo.ts
import * as anchor from "@coral-xyz/anchor";
import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  getAccount as getSplAccount,
} from "@solana/spl-token";
import fs from "fs";
import path from "path";

const RPC = "http://127.0.0.1:8899";
const PROGRAM_ID = new PublicKey("6WnjPtMbz6ogoJg2PgGnbnyEW4uEmPV6EqzLQ4BqouPo");

const idlPath = path.resolve(__dirname, "../target/idl/energy_token_program.json");
const idl = JSON.parse(fs.readFileSync(idlPath, "utf8"));

const STATE_PDA = PublicKey.findProgramAddressSync([Buffer.from("state")], PROGRAM_ID)[0];
const MINT_AUTH_PDA = PublicKey.findProgramAddressSync([Buffer.from("mint_auth")], PROGRAM_ID)[0];

function buildProvider() {
  const connection = new Connection(RPC, "confirmed");
  const home = process.env.HOME || process.env.USERPROFILE!;
  const secret = JSON.parse(fs.readFileSync(path.join(home, ".config/solana/id.json"), "utf8"));
  const payer = Keypair.fromSecretKey(Uint8Array.from(secret));
  const wallet = new anchor.Wallet(payer);
  const provider = new anchor.AnchorProvider(connection, wallet, { commitment: "confirmed" });
  return { connection, payer, provider, wallet };
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

async function main() {
  const { connection, payer, wallet } = buildProvider();

  console.log("Program:", PROGRAM_ID.toBase58());
  console.log("Oracle (payer):", wallet.publicKey.toBase58());
  console.log("STATE PDA:", STATE_PDA.toBase58());
  console.log("MINT AUTH PDA:", MINT_AUTH_PDA.toBase58());

  const user = Keypair.generate();
  await connection.requestAirdrop(user.publicKey, 1e9);
  console.log("User:", user.publicKey.toBase58());

  // Determine the mint (initialize if needed)
  let mint: PublicKey;
  const freshMint = Keypair.generate();
  try {
    console.log("\nInitializing program state + mint...");
    const keys = [
      { pubkey: STATE_PDA, isSigner: false, isWritable: true },
      { pubkey: freshMint.publicKey, isSigner: true, isWritable: true },
      { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const initIxName = pickIxName("initialize", "initialize");
    const data = encodeIx(initIxName, { oracle: wallet.publicKey });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
    const sig = await sendTx(connection, payer, ix, [freshMint]);
    console.log("Initialized ✅ tx:", sig);
    mint = freshMint.publicKey;
  } catch (e: any) {
    console.log("Initialize likely already done:", e.message);
    const state = await fetchState(connection);
    if (!state) throw new Error("State account not found; reset local validator if needed.");
    mint = new PublicKey(state.mint);
    console.log("Using existing mint:", mint.toBase58());
  }

  // ✅ Compute user ATA *before* using it in any keys arrays
  const userAta = await getAssociatedTokenAddress(mint, user.publicKey);

  // Mint 5 to user
  console.log("\nMinting 5 tokens to user...");
  {
    const keys = [
      { pubkey: STATE_PDA, isSigner: false, isWritable: true },
      { pubkey: mint, isSigner: false, isWritable: true },
      { pubkey: MINT_AUTH_PDA, isSigner: false, isWritable: false },
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: userAta, isSigner: false, isWritable: true },
      { pubkey: user.publicKey, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const mintIxName = pickIxName("mint_energy", "mintEnergy");
    const data = encodeIx(mintIxName, { amount: new anchor.BN(5) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
    const sig = await sendTx(connection, payer, ix);
    console.log("Minted 5 ✅ tx:", sig);
  }

  let acc = await getSplAccount(connection, userAta);
  console.log("User balance after mint:", Number(acc.amount)); // expect 5

  // Burn 2 from user (note: mint must be writable)
  console.log("\nBurning 2 tokens from user...");
  {
    const keys = [
      { pubkey: mint, isSigner: false, isWritable: true },  // <-- writable!
      { pubkey: userAta, isSigner: false, isWritable: true },
      { pubkey: user.publicKey, isSigner: true, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ];
    const burnIxName = pickIxName("burn_energy", "burnEnergy");
    const data = encodeIx(burnIxName, { amount: new anchor.BN(2) });
    const ix = new TransactionInstruction({ programId: PROGRAM_ID, keys, data });
    const sig = await sendTx(connection, payer, ix, [user]);
    console.log("Burned 2 ✅ tx:", sig);
  }

  acc = await getSplAccount(connection, userAta);
  console.log("User balance after burn:", Number(acc.amount)); // expect 3

  console.log("\nDone ✅");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
