import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { P2pEnergySwap } from "../target/types/p2p_energy_swap";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
} from "@solana/spl-token";
import assert from "assert";

describe("p2p_energy_swap", () => {
  // Configure the client
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.P2pEnergySwap as Program<P2pEnergySwap>;

  // Test keys
  const oracle = Keypair.generate();
  const buyer = Keypair.generate();

  // Store addresses
  let marketplace: PublicKey;
  let eKwhMint: PublicKey;
  let sellerTokenAccount: PublicKey;
  let buyerTokenAccount: PublicKey;
  let escrowTokenAccount: PublicKey;
  let offer: PublicKey;
  let escrow: PublicKey;

  it("Initialize Marketplace", async () => {
    const marketplaceKP = Keypair.generate();
    marketplace = marketplaceKP.publicKey;

    await program.methods
      .initializeMarketplace(oracle.publicKey)
      .accounts({
        marketplace: marketplace,
        admin: provider.wallet.publicKey,
        oracle: oracle.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([marketplaceKP])
      .rpc();

    const account = await program.account.marketplace.fetch(marketplace);
    assert.equal(account.oracle.toBase58(), oracle.publicKey.toBase58());
    console.log("✅ Marketplace initialized with oracle:", account.oracle.toBase58());
  });

  it("Create eKWh Mint and Accounts", async () => {
    // Create mint with 0 decimals (1 token = 1 kWh)
    eKwhMint = await createMint(
      provider.connection,
      provider.wallet.payer,
      provider.wallet.publicKey,
      null,
      0
    );

    // Seller ATA
    const sellerATA = await getOrCreateAssociatedTokenAccount(
      provider.connection,
      provider.wallet.payer,
      eKwhMint,
      provider.wallet.publicKey
    );
    sellerTokenAccount = sellerATA.address;

    // Buyer ATA
    const buyerATA = await getOrCreateAssociatedTokenAccount(
      provider.connection,
      provider.wallet.payer,
      eKwhMint,
      buyer.publicKey
    );
    buyerTokenAccount = buyerATA.address;

    // Mint 100 tokens (kWh) to seller
    await mintTo(
      provider.connection,
      provider.wallet.payer,
      eKwhMint,
      sellerTokenAccount,
      provider.wallet.payer,
      100
    );

    console.log("✅ eKWh mint created:", eKwhMint.toBase58());
    console.log("Seller ATA:", sellerTokenAccount.toBase58());
    console.log("Buyer ATA:", buyerTokenAccount.toBase58());
  });

  it("Oracle mints new energy tokens", async () => {
    // Just for testing, oracle mints 10 extra tokens to buyer
    await program.methods
      .mintEnergy(new anchor.BN(10))
      .accounts({
        marketplace,
        mint: eKwhMint,
        recipientTokens: buyerTokenAccount,
        oracle: oracle.publicKey,
        tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
      })
      .signers([oracle])
      .rpc();

    console.log("✅ Oracle minted 10 tokens to buyer");
  });

  it("Create Offer", async () => {
    const offerKP = Keypair.generate();
    offer = offerKP.publicKey;

    // For simplicity we reuse seller ATA and manually pass escrow as a new ATA
    const escrowATA = await getOrCreateAssociatedTokenAccount(
      provider.connection,
      provider.wallet.payer,
      eKwhMint,
      provider.wallet.publicKey // program will need a PDA here in production
    );
    escrowTokenAccount = escrowATA.address;

    await program.methods
      .createOffer(new anchor.BN(5), new anchor.BN(200)) // 5 kWh at price=200
      .accounts({
        seller: provider.wallet.publicKey,
        offer: offer,
        sellerTokens: sellerTokenAccount,
        escrowTokens: escrowTokenAccount,
        escrowAuthority: provider.wallet.publicKey,
        tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .signers([offerKP])
      .rpc();

    const account = await program.account.offer.fetch(offer);
    assert.ok(account.isActive);
    console.log("✅ Offer created:", account.amount.toString(), "tokens");
  });

  it("Accept Offer", async () => {
    const escrowKP = Keypair.generate();
    escrow = escrowKP.publicKey;

    await program.methods
      .acceptOffer()
      .accounts({
        escrow,
        offer,
        buyer: buyer.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([escrowKP, buyer])
      .rpc();

    const account = await program.account.escrow.fetch(escrow);
    assert.equal(account.buyer.toBase58(), buyer.publicKey.toBase58());
    console.log("✅ Buyer accepted offer");
  });

  it("Oracle confirms delivery", async () => {
    await program.methods
      .confirmDelivery()
      .accounts({
        marketplace,
        offer,
        escrow,
        buyerTokens: buyerTokenAccount,
        escrowTokens: escrowTokenAccount,
        oracle: oracle.publicKey,
        tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
      })
      .signers([oracle])
      .rpc();

    const account = await program.account.offer.fetch(offer);
    assert.ok(!account.isActive);
    console.log("✅ Delivery confirmed and tokens released to buyer");
  });

  it("Oracle burns tokens after consumption", async () => {
    await program.methods
      .burnEnergy(new anchor.BN(3)) // burn 3 tokens
      .accounts({
        marketplace,
        mint: eKwhMint,
        userTokens: buyerTokenAccount,
        oracle: oracle.publicKey,
        tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
      })
      .signers([oracle])
      .rpc();

    console.log("✅ Oracle burned 3 tokens from buyer after consumption");
  });
});
