use anchor_lang::prelude::*;
use anchor_lang::solana_program::{program::invoke, system_instruction};
use anchor_spl::associated_token::AssociatedToken;
use anchor_spl::token::{
    self, Burn, CloseAccount, Mint, MintTo, Token, TokenAccount, Transfer,
};

declare_id!("6WnjPtMbz6ogoJg2PgGnbnyEW4uEmPV6EqzLQ4BqouPo"); // replace with your actual program id

#[program]
pub mod energy_token_program {
    use super::*;

    /// One-time setup:
    /// - Creates a 0-decimals EnergyToken mint
    /// - Sets PDA `mint_auth` as mint & freeze authority
    /// - Stores `oracle` pubkey in State
  pub fn initialize(ctx: Context<Initialize>, oracle: Pubkey) -> Result<()> {
    let state = &mut ctx.accounts.state;

    // Always record the mint we’re being called with (idempotent).
    state.mint = ctx.accounts.mint.key();

    // Allow the caller to (re)set the oracle each time initialize is invoked.
    // This makes tests independent: each file can set the oracle it will use.
    state.oracle = oracle;

    Ok(())
}

    /// Oracle mints `amount` tokens to recipient’s ATA (1 token = 1 kWh).
    pub fn mint_energy(ctx: Context<MintEnergy>, amount: u64) -> Result<()> {
        require!(amount > 0, EnergyError::InvalidAmount);
        require_keys_eq!(ctx.accounts.state.oracle, ctx.accounts.oracle.key());
        require_keys_eq!(ctx.accounts.state.mint, ctx.accounts.mint.key());

        // PDA signer for mint authority (stable locals for seeds)
        let bump = ctx.bumps.mint_authority;
        let bump_bytes = [bump];
        let seed_auth = b"mint_auth";
        let seeds: [&[u8]; 2] = [seed_auth.as_ref(), &bump_bytes];
        let signers: [&[&[u8]]; 1] = [&seeds];

        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            MintTo {
                mint: ctx.accounts.mint.to_account_info(),
                to: ctx.accounts.recipient_ata.to_account_info(),
                authority: ctx.accounts.mint_authority.to_account_info(),
            },
            &signers,
        );
        token::mint_to(cpi_ctx, amount)?;
        Ok(())
    }

    /// User burns their own tokens when consuming energy.
    pub fn burn_energy(ctx: Context<BurnEnergy>, amount: u64) -> Result<()> {
        require!(amount > 0, EnergyError::InvalidAmount);

        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Burn {
                mint: ctx.accounts.mint.to_account_info(),
                from: ctx.accounts.user_ata.to_account_info(),
                authority: ctx.accounts.user.to_account_info(),
            },
        );
        token::burn(cpi_ctx, amount)?;
        Ok(())
    }

    // -------------------- Marketplace: Create Sell Order --------------------

    /// Create a sell order and escrow tokens into a PDA-owned vault ATA.
    /// Seeds:
    /// - order PDA: ["order", seller, mint, order_nonce_le]
    /// - vault authority PDA: ["vault-auth", order_pda]
    pub fn create_sell_order(
        ctx: Context<CreateSellOrder>,
        order_nonce: u64,
        amount: u64,
        price_lamports_per_token: u64,
    ) -> Result<()> {
        require!(amount > 0, EnergyError::InvalidAmount);

        // record bumps (struct fields on Anchor 0.31)
        let order_bump = ctx.bumps.order;
        let vault_auth_bump = ctx.bumps.vault_authority;

        // move seller tokens -> vault ATA (escrow)
        let cpi_accounts = Transfer {
            from: ctx.accounts.seller_token.to_account_info(),
            to: ctx.accounts.vault_ata.to_account_info(),
            authority: ctx.accounts.seller.to_account_info(),
        };
        let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
        token::transfer(cpi_ctx, amount)?;

        // save order state
        let order = &mut ctx.accounts.order;
        order.seller = ctx.accounts.seller.key();
        order.mint = ctx.accounts.mint.key();
        order.price_lamports_per_token = price_lamports_per_token;
        order.amount_remaining = amount;
        order.active = true;
        order.order_nonce = order_nonce;
        order.order_bump = order_bump;
        order.vault_auth_bump = vault_auth_bump;

        Ok(())
    }

    // -------------------- Marketplace: Fill Sell Order --------------------

    /// Buyer fills qty from an active order: pays SOL to seller, receives tokens from vault.
    pub fn fill_sell_order(ctx: Context<FillSellOrder>, qty: u64) -> Result<()> {
        require!(qty > 0, EnergyError::InvalidAmount);

        // Read from order immutably in a short scope to avoid aliasing with later &mut
        let (order_key, price, mut_remaining, active, bump) = {
            let o = &ctx.accounts.order;
            (o.key(), o.price_lamports_per_token, o.amount_remaining, o.active, o.vault_auth_bump)
        };
        require!(active, EnergyError::InactiveOrder);
        require!(mut_remaining >= qty, EnergyError::InsufficientOrderAmount);

        // cost = qty * price (checked)
        let cost = qty
            .checked_mul(price)
            .ok_or(EnergyError::MathOverflow)?;

        // transfer SOL from buyer -> seller
        let ix = system_instruction::transfer(
            &ctx.accounts.buyer.key(),
            &ctx.accounts.seller.key(),
            cost,
        );
        invoke(
            &ix,
            &[
                ctx.accounts.buyer.to_account_info(),
                ctx.accounts.seller.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
            ],
        )?;

        // transfer tokens vault -> buyer (vault_authority PDA signs)
        let order_key_bytes = order_key.as_ref();
        let bump_bytes = [bump];
        let tag = b"vault-auth";
        let seeds: [&[u8]; 3] = [tag.as_ref(), order_key_bytes, &bump_bytes];
        let signers: [&[&[u8]]; 1] = [&seeds];

        let cpi_accounts = Transfer {
            from: ctx.accounts.vault_ata.to_account_info(),
            to: ctx.accounts.buyer_token.to_account_info(),
            authority: ctx.accounts.vault_authority.to_account_info(),
        };
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            &signers,
        );
        token::transfer(cpi_ctx, qty)?;

        // Now update order mutably
        let order = &mut ctx.accounts.order;
        order.amount_remaining = mut_remaining - qty;
        if order.amount_remaining == 0 {
            order.active = false;
        }

        Ok(())
    }

    // -------------------- Marketplace: Cancel Sell Order --------------------

    /// Seller cancels order, gets remaining tokens back, closes vault & order.
    pub fn cancel_sell_order(ctx: Context<CancelSellOrder>) -> Result<()> {
        // Precompute seeds safely (immutable)
        let (order_key, bump) = {
            let o = &ctx.accounts.order;
            (o.key(), o.vault_auth_bump)
        };
        let order_key_bytes = order_key.as_ref();
        let bump_bytes = [bump];
        let tag = b"vault-auth";
        let seeds: [&[u8]; 3] = [tag.as_ref(), order_key_bytes, &bump_bytes];
        let signers: [&[&[u8]]; 1] = [&seeds];

        // return any remaining tokens to seller
        if ctx.accounts.vault_ata.amount > 0 {
            let cpi_accounts = Transfer {
                from: ctx.accounts.vault_ata.to_account_info(),
                to: ctx.accounts.seller_token.to_account_info(),
                authority: ctx.accounts.vault_authority.to_account_info(),
            };
            let cpi_ctx = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                cpi_accounts,
                &signers,
            );
            token::transfer(cpi_ctx, ctx.accounts.vault_ata.amount)?;
        }

        // close vault ATA (rent -> seller)
        let cpi_accounts = CloseAccount {
            account: ctx.accounts.vault_ata.to_account_info(),
            destination: ctx.accounts.seller.to_account_info(),
            authority: ctx.accounts.vault_authority.to_account_info(),
        };
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            &signers,
        );
        token::close_account(cpi_ctx)?;

        // order is closed by `close = seller` constraint
        Ok(())
    }
}

/* -------------------- Core State -------------------- */

#[account]
pub struct State {
    pub mint: Pubkey,
    pub oracle: Pubkey,
}

/* -------------------- Core Accounts -------------------- */

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init_if_needed,
        payer = authority,
        space = 8 + 32 + 32,
        seeds = [b"state"],
        bump
    )]
    pub state: Account<'info, State>,

    #[account(
        init_if_needed,
        payer = authority,
        mint::decimals = 0,
        mint::authority = mint_authority,
        mint::freeze_authority = mint_authority
    )]
    pub mint: Account<'info, Mint>,

    /// CHECK: PDA used only as a signer for mint authority
    #[account(seeds = [b"mint_auth"], bump)]
    pub mint_authority: UncheckedAccount<'info>,

    /// Payer for `state` and `mint`
    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct MintEnergy<'info> {
    #[account(mut, seeds = [b"state"], bump)]
    pub state: Account<'info, State>,

    #[account(mut, address = state.mint)]
    pub mint: Account<'info, Mint>,

    /// CHECK: PDA signer that is mint authority
    #[account(seeds = [b"mint_auth"], bump)]
    pub mint_authority: UncheckedAccount<'info>,

    /// Oracle pays to create recipient ATA if needed → must be `mut`
    #[account(mut)]
    pub oracle: Signer<'info>,

    /// Recipient ATA (auto-created if missing; payer = oracle)
    #[account(
        init_if_needed,
        payer = oracle,
        associated_token::mint = mint,
        associated_token::authority = recipient
    )]
    pub recipient_ata: Account<'info, TokenAccount>,

    /// CHECK: Only used as the ATA owner
    pub recipient: UncheckedAccount<'info>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct BurnEnergy<'info> {
    pub mint: Account<'info, Mint>,

    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = user
    )]
    pub user_ata: Account<'info, TokenAccount>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub token_program: Program<'info, Token>,
}

/* -------------------- Marketplace State -------------------- */

#[account]
pub struct SellOrder {
    /// Seller (lamports recipient; canceller)
    pub seller: Pubkey,
    /// Energy token mint (decimals = 0)
    pub mint: Pubkey,
    /// Price in lamports per token
    pub price_lamports_per_token: u64,
    /// Remaining amount in tokens
    pub amount_remaining: u64,
    /// True while order is fillable
    pub active: bool,
    /// Nonce used in order PDA seeds
    pub order_nonce: u64,
    /// PDA bump for order
    pub order_bump: u8,
    /// PDA bump for vault authority
    pub vault_auth_bump: u8,
}
impl SellOrder {
    pub const LEN: usize = 8 /*disc*/
        + 32 /*seller*/
        + 32 /*mint*/
        + 8  /*price*/
        + 8  /*remaining*/
        + 1  /*active*/
        + 8  /*nonce*/
        + 1  /*order_bump*/
        + 1; /*vault_auth_bump*/
}

/* -------------------- Marketplace Accounts -------------------- */

/// Create Sell Order
#[derive(Accounts)]
#[instruction(order_nonce: u64, amount: u64, price_lamports_per_token: u64)]
pub struct CreateSellOrder<'info> {
    /// Seller creates order; pays rent; sends tokens
    #[account(mut)]
    pub seller: Signer<'info>,

    /// Seller's token account (debited)
    #[account(
        mut,
        constraint = seller_token.owner == seller.key(),
        constraint = seller_token.mint == mint.key(),
    )]
    pub seller_token: Account<'info, TokenAccount>,

    /// Order PDA: ["order", seller, mint, order_nonce_le]
    #[account(
        init,
        payer = seller,
        space = SellOrder::LEN,
        seeds = [
            b"order",
            seller.key().as_ref(),
            mint.key().as_ref(),
            &order_nonce.to_le_bytes()
        ],
        bump
    )]
    pub order: Account<'info, SellOrder>,

    /// Vault authority PDA: ["vault-auth", order_pda]
    #[account(
        seeds = [b"vault-auth", order.key().as_ref()],
        bump
    )]
    /// CHECK: PDA signer only
    pub vault_authority: UncheckedAccount<'info>,

    /// Vault ATA owned by vault_authority (escrow)
    #[account(
        init,
        payer = seller,
        associated_token::mint = mint,
        associated_token::authority = vault_authority
    )]
    pub vault_ata: Account<'info, TokenAccount>,

    /// Energy token mint
    pub mint: Account<'info, Mint>,

    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

/// Fill Sell Order
#[derive(Accounts)]
pub struct FillSellOrder<'info> {
    /// Buyer pays SOL & receives tokens
    #[account(mut)]
    pub buyer: Signer<'info>,

    /// Buyer's ATA (auto-create if missing)
    #[account(
        init_if_needed,
        payer = buyer,
        associated_token::mint = mint,
        associated_token::authority = buyer
    )]
    pub buyer_token: Account<'info, TokenAccount>,

    /// Seller (lamports recipient) must match order.seller
    /// CHECK: validated via address constraint
    #[account(mut, address = order.seller)]
    pub seller: UncheckedAccount<'info>,

    #[account(
        mut,
        has_one = mint,
        constraint = order.active == true @ EnergyError::InactiveOrder
    )]
    pub order: Account<'info, SellOrder>,

    /// Vault authority PDA: ["vault-auth", order_pda]
    #[account(
        seeds = [b"vault-auth", order.key().as_ref()],
        bump = order.vault_auth_bump
    )]
    /// CHECK: PDA signer only
    pub vault_authority: UncheckedAccount<'info>,

    /// Vault ATA holding escrowed tokens
    #[account(
        mut,
        constraint = vault_ata.mint == mint.key(),
        constraint = vault_ata.owner == vault_authority.key(),
    )]
    pub vault_ata: Account<'info, TokenAccount>,

    pub mint: Account<'info, Mint>,

    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

/// Cancel Sell Order
#[derive(Accounts)]
pub struct CancelSellOrder<'info> {
    /// Seller must sign; receives rent and remaining tokens
    #[account(mut)]
    pub seller: Signer<'info>,

    #[account(
        mut,
        has_one = mint,
        constraint = order.seller == seller.key() @ EnergyError::Unauthorized,
        close = seller
    )]
    pub order: Account<'info, SellOrder>,

    /// Vault authority PDA
    #[account(
        seeds = [b"vault-auth", order.key().as_ref()],
        bump = order.vault_auth_bump
    )]
    /// CHECK: PDA signer only
    pub vault_authority: UncheckedAccount<'info>,

    /// Vault ATA to drain & close
    #[account(
        mut,
        constraint = vault_ata.mint == mint.key(),
        constraint = vault_ata.owner == vault_authority.key(),
    )]
    pub vault_ata: Account<'info, TokenAccount>,

    /// Seller's ATA to receive remaining tokens
    #[account(
        mut,
        constraint = seller_token.mint == mint.key(),
        constraint = seller_token.owner == seller.key(),
    )]
    pub seller_token: Account<'info, TokenAccount>,

    pub mint: Account<'info, Mint>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

/* -------------------- Errors -------------------- */

#[error_code]
pub enum EnergyError {
    #[msg("Amount must be > 0")]
    InvalidAmount,
    // Marketplace
    #[msg("Order is not active")]
    InactiveOrder,
    #[msg("Insufficient order amount")]
    InsufficientOrderAmount,
    #[msg("Arithmetic overflow")]
    MathOverflow,
    #[msg("Unauthorized")]
    Unauthorized,
}
