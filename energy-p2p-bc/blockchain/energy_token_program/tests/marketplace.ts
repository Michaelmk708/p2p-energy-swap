import * as anchor from "@coral-xyz/anchor";
import { Program, BN } from "@coral-xyz/anchor";
import {
  getAccount,
  getAssociatedTokenAddressSync,
  TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import {
  Keypair,
  LAMPORTS_PER_SOL,
  PublicKey,
  SystemProgram,
} from "@solana/web3.js";
import { assert } from "chai";

describe("marketplace", () => {
  const provider = anchor.AnchorProvider.local();
  anchor.setProvider(provider);

  // @ts-ignore adjust name if your IDL key differs
  const program = anchor.workspace.EnergyTokenProgram as Program;

  const authority = provider.wallet as anchor.Wallet;
  const oracle = Keypair.generate();
  const seller = Keypair.generate();
  const buyer = Keypair.generate();

  let statePda: PublicKey;
  let mintAuthPda: PublicKey;
  let mint: PublicKey;

  let sellerAta: PublicKey;
  let buyerAta: PublicKey;

  let orderPda: PublicKey;
  let vaultAuthPda: PublicKey;
  let vaultAta: PublicKey;

  const ORDER_NONCE = new BN(7);
  const SELL_AMOUNT = new BN(10);
  const PRICE = new BN(2_000_000); // 0.002 SOL
  const FILL_QTY = new BN(4);

  it("setup: airdrop & initialize program (idempotent)", async () => {
    // fund non-provider keypairs
    for (const kp of [oracle, seller, buyer]) {
      const sig = await provider.connection.requestAirdrop(
        kp.publicKey,
        5 * LAMPORTS_PER_SOL
      );
      await provider.connection.confirmTransaction(sig, "confirmed");
    }

    // PDAs
    [statePda] = PublicKey.findProgramAddressSync(
      [Buffer.from("state")],
      program.programId
    );
    [mintAuthPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("mint_auth")],
      program.programId
    );

    // ALWAYS create a fresh mint each run and sign with its keypair.
    const mintKp = Keypair.generate();
    mint = mintKp.publicKey;

    await program.methods
      .initialize(oracle.publicKey) // sets state.mint + state.oracle
      .accounts({
        state: statePda,
        mint,
        mintAuthority: mintAuthPda,
        authority: authority.publicKey,
        systemProgram: SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: new PublicKey(
          "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        ),
      })
      .signers([mintKp]) // <- ALWAYS sign; avoids “Missing signature …”
      .rpc();

    // ATAs
    sellerAta = getAssociatedTokenAddressSync(mint, seller.publicKey);
    buyerAta = getAssociatedTokenAddressSync(mint, buyer.publicKey);
  });

  it("mint_energy to seller via oracle", async () => {
    await program.methods
      .mintEnergy(SELL_AMOUNT)
      .accounts({
        state: statePda,
        mint,
        mintAuthority: mintAuthPda,
        oracle: oracle.publicKey,
        recipientAta: sellerAta,
        recipient: seller.publicKey,
        systemProgram: SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: new PublicKey(
          "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        ),
      })
      .signers([oracle])
      .rpc();

    const sAcc = await getAccount(provider.connection, sellerAta);
    assert.equal(Number(sAcc.amount), SELL_AMOUNT.toNumber());
  });

  it("derive order & vault PDAs", async () => {
    const le = Buffer.alloc(8);
    le.writeBigUInt64LE(BigInt(ORDER_NONCE.toString()));

    [orderPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("order"), seller.publicKey.toBuffer(), mint.toBuffer(), le],
      program.programId
    );
    [vaultAuthPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("vault-auth"), orderPda.toBuffer()],
      program.programId
    );
    vaultAta = getAssociatedTokenAddressSync(mint, vaultAuthPda, true);
  });

  it("create_sell_order (escrow tokens)", async () => {
    await program.methods
      .createSellOrder(ORDER_NONCE, SELL_AMOUNT, PRICE)
      .accounts({
        seller: seller.publicKey,
        sellerToken: sellerAta, // exact camelCase
        order: orderPda,
        vaultAuthority: vaultAuthPda,
        vaultAta: vaultAta,
        mint,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: new PublicKey(
          "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        ),
        systemProgram: SystemProgram.programId,
      })
      .signers([seller])
      .rpc();

    const v = await getAccount(provider.connection, vaultAta);
    const s = await getAccount(provider.connection, sellerAta);
    assert.equal(Number(v.amount), SELL_AMOUNT.toNumber());
    assert.equal(Number(s.amount), 0);
  });

  it("fill_sell_order (buyer pays SOL & receives tokens)", async () => {
    const buyerSolBefore = await provider.connection.getBalance(buyer.publicKey);
    const sellerSolBefore = await provider.connection.getBalance(seller.publicKey);

    await program.methods
      .fillSellOrder(FILL_QTY)
      .accounts({
        buyer: buyer.publicKey,
        buyerToken: buyerAta,
        seller: seller.publicKey,
        order: orderPda,
        vaultAuthority: vaultAuthPda,
        vaultAta: vaultAta,
        mint,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: new PublicKey(
          "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        ),
        systemProgram: SystemProgram.programId,
      })
      .signers([buyer])
      .rpc();

    const b = await getAccount(provider.connection, buyerAta);
    const v = await getAccount(provider.connection, vaultAta);
    assert.equal(Number(b.amount), FILL_QTY.toNumber());
    assert.equal(
      Number(v.amount),
      SELL_AMOUNT.sub(FILL_QTY).toNumber()
    );

    const buyerSolAfter = await provider.connection.getBalance(buyer.publicKey);
    const sellerSolAfter = await provider.connection.getBalance(seller.publicKey);
    const cost = FILL_QTY.mul(PRICE).toNumber();
    assert.isTrue(buyerSolBefore - buyerSolAfter >= cost);
    assert.isTrue(sellerSolAfter - sellerSolBefore >= cost);
  });

  it("cancel_sell_order (return remaining & close)", async () => {
    await program.methods
      .cancelSellOrder()
      .accounts({
        seller: seller.publicKey,
        order: orderPda,
        vaultAuthority: vaultAuthPda,
        vaultAta: vaultAta,
        sellerToken: sellerAta, // exact camelCase
        mint,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .signers([seller])
      .rpc();

    const vInfo = await provider.connection.getAccountInfo(vaultAta);
    assert.isNull(vInfo);

    const oInfo = await provider.connection.getAccountInfo(orderPda);
    assert.isNull(oInfo);

    const s = await getAccount(provider.connection, sellerAta);
    assert.equal(Number(s.amount), SELL_AMOUNT.sub(FILL_QTY).toNumber());
  });
});
