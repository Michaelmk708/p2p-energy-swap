use anchor_lang::prelude::*;
use anchor_spl::token::{
    self, Mint, Token, TokenAccount, Transfer, MintTo, Burn,
};

declare_id!("YourProgramIDHere"); // replace after build

#[program]
pub mod p2p_energy_swap {
    use super::*;

    // -----------------
    // Marketplace Setup
    // -----------------
    pub fn initialize_marketplace(
        ctx: Context<InitializeMarketplace>,
        oracle: Pubkey,
    ) -> Result<()> {
        let marketplace = &mut ctx.accounts.marketplace;
        marketplace.admin = ctx.accounts.admin.key();
        marketplace.oracle = oracle;
        Ok(())
    }

    // -----------------
    // Mint tokens (Oracle only)
    // -----------------
    pub fn mint_energy(
        ctx: Context<MintEnergy>,
        amount: u64,
    ) -> Result<()> {
        let marketplace = &ctx.accounts.marketplace;
        require_keys_eq!(marketplace.oracle, ctx.accounts.oracle.key(), CustomError::Unauthorized);

        let cpi_accounts = MintTo {
            mint: ctx.accounts.mint.to_account_info(),
            to: ctx.accounts.recipient_tokens.to_account_info(),
            authority: ctx.accounts.oracle.to_account_info(),
        };
        let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
        token::mint_to(cpi_ctx, amount)?;
        Ok(())
    }

    // -----------------
    // Burn tokens (Oracle only)
    // -----------------
    pub fn burn_energy(
        ctx: Context<BurnEnergy>,
        amount: u64,
    ) -> Result<()> {
        let marketplace = &ctx.accounts.marketplace;
        require_keys_eq!(marketplace.oracle, ctx.accounts.oracle.key(), CustomError::Unauthorized);

        let cpi_accounts = Burn {
            mint: ctx.accounts.mint.to_account_info(),
            from: ctx.accounts.user_tokens.to_account_info(),
            authority: ctx.accounts.oracle.to_account_info(),
        };
        let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
        token::burn(cpi_ctx, amount)?;
        Ok(())
    }

    // -----------------
    // Create an offer (seller → escrow)
    // -----------------
    pub fn create_offer(
        ctx: Context<CreateOffer>,
        amount: u64,
        price: u64,
    ) -> Result<()> {
        let offer = &mut ctx.accounts.offer;
        offer.seller = ctx.accounts.seller.key();
        offer.amount = amount;
        offer.price = price;
        offer.is_active = true;

        // transfer seller tokens → escrow
        token::transfer(
            ctx.accounts.into_transfer_to_escrow_context(),
            amount,
        )?;
        Ok(())
    }

    // -----------------
    // Buyer accepts offer
    // -----------------
    pub fn accept_offer(ctx: Context<AcceptOffer>) -> Result<()> {
        let offer = &mut ctx.accounts.offer;
        require!(offer.is_active, CustomError::InactiveOffer);

        let escrow = &mut ctx.accounts.escrow;
        escrow.buyer = ctx.accounts.buyer.key();
        escrow.offer = offer.key();
        escrow.is_paid = false;

        Ok(())
    }

    // -----------------
    // Oracle confirms delivery
    // -----------------
    pub fn confirm_delivery(ctx: Context<ConfirmDelivery>) -> Result<()> {
        let marketplace = &ctx.accounts.marketplace;
        require_keys_eq!(marketplace.oracle, ctx.accounts.oracle.key(), CustomError::Unauthorized);

        let offer = &mut ctx.accounts.offer;
        let escrow = &mut ctx.accounts.escrow;

        require!(offer.is_active, CustomError::InactiveOffer);

        // transfer escrow → buyer
        token::transfer(
            ctx.accounts.into_transfer_to_buyer_context(),
            offer.amount,
        )?;

        offer.is_active = false;
        escrow.is_paid = true;

        Ok(())
    }
}

# -----------------
# Accounts
# -----------------

#[account]
pub struct Marketplace {
    pub admin: Pubkey,
    pub oracle: Pubkey,
}

#[account]
pub struct Offer {
    pub seller: Pubkey,
    pub amount: u64,
    pub price: u64,
    pub is_active: bool,
}

#[account]
pub struct Escrow {
    pub buyer: Pubkey,
    pub offer: Pubkey,
    pub is_paid: bool,
}

# -----------------
# Instruction Contexts
# -----------------

#[derive(Accounts)]
pub struct InitializeMarketplace<'info> {
    #[account(init, payer = admin, space = 8 + 32 + 32)]
    pub marketplace: Account<'info, Marketplace>,

    #[account(mut)]
    pub admin: Signer<'info>,
    /// CHECK: Oracle authority
    pub oracle: UncheckedAccount<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintEnergy<'info> {
    #[account(mut)]
    pub marketplace: Account<'info, Marketplace>,
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub recipient_tokens: Account<'info, TokenAccount>,
    pub oracle: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct BurnEnergy<'info> {
    #[account(mut)]
    pub marketplace: Account<'info, Marketplace>,
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub user_tokens: Account<'info, TokenAccount>,
    pub oracle: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct CreateOffer<'info> {
    #[account(mut)]
    pub seller: Signer<'info>,

    #[account(init, payer = seller, space = 8 + 32 + 8 + 8 + 1)]
    pub offer: Account<'info, Offer>,

    #[account(mut)]
    pub seller_tokens: Account<'info, TokenAccount>,
    #[account(mut)]
    pub escrow_tokens: Account<'info, TokenAccount>,

    pub escrow_authority: UncheckedAccount<'info>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

impl<'info> CreateOffer<'info> {
    fn into_transfer_to_escrow_context(&self) -> CpiContext<'_, '_, '_, 'info, Transfer<'info>> {
        let cpi_accounts = Transfer {
            from: self.seller_tokens.to_account_info(),
            to: self.escrow_tokens.to_account_info(),
            authority: self.seller.to_account_info(),
        };
        CpiContext::new(self.token_program.to_account_info(), cpi_accounts)
    }
}

#[derive(Accounts)]
pub struct AcceptOffer<'info> {
    #[account(init, payer = buyer, space = 8 + 32 + 32 + 1)]
    pub escrow: Account<'info, Escrow>,
    pub offer: Account<'info, Offer>,
    #[account(mut)]
    pub buyer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ConfirmDelivery<'info> {
    pub marketplace: Account<'info, Marketplace>,
    #[account(mut)]
    pub offer: Account<'info, Offer>,
    #[account(mut)]
    pub escrow: Account<'info, Escrow>,
    #[account(mut)]
    pub buyer_tokens: Account<'info, TokenAccount>,
    #[account(mut)]
    pub escrow_tokens: Account<'info, TokenAccount>,
    pub oracle: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

impl<'info> ConfirmDelivery<'info> {
    fn into_transfer_to_buyer_context(&self) -> CpiContext<'_, '_, '_, 'info, Transfer<'info>> {
        let cpi_accounts = Transfer {
            from: self.escrow_tokens.to_account_info(),
            to: self.buyer_tokens.to_account_info(),
            authority: self.oracle.to_account_info(),
        };
        CpiContext::new(self.token_program.to_account_info(), cpi_accounts)
    }
}

# -----------------
# Custom Errors
# -----------------

#[error_code]
pub enum CustomError {
    #[msg("Unauthorized caller")]
    Unauthorized,
    #[msg("Offer is not active")]
    InactiveOffer,
}
