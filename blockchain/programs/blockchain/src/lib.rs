use anchor_lang::prelude::*;

// This is your unique Program ID. Anchor auto-generates this.
declare_id!("8fcb4XuybVfKTAJZvUZfdRtgRSQnSdikJod3yKu9iHhB"); 

#[program]
pub mod p2p_energy_swap {
    use super::*;

    // 1. Initialize the Estate's Energy Ledger
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let stats = &mut ctx.accounts.stats;
        stats.total_trades = 0;
        stats.total_kwh_traded = 0;
        msg!("P2P Energy Swap Ledger Initialized!");
        Ok(())
    }

    // 2. Record a Trade (Called by your Django Backend/Hardware Oracle)
    pub fn record_trade(
        ctx: Context<RecordTrade>, 
        buyer: String, 
        seller: String, 
        amount_kwh: u64, 
        price_kes: u64
    ) -> Result<()> {
        let stats = &mut ctx.accounts.stats;
        
        // Update global estate statistics
        stats.total_trades += 1;
        stats.total_kwh_traded += amount_kwh;

        // Emit an Immutable Event to the Blockchain (The Audit Trail)
      // Emit an Immutable Event to the Blockchain (The Audit Trail)
        emit!(TradeEvent {
            buyer: buyer.clone(),    // <--- Add .clone() here
            seller: seller.clone(),  // <--- Add .clone() here
            amount_kwh,
            price_kes,
            timestamp: Clock::get()?.unix_timestamp,
        });

        // Now this line will work perfectly!
        msg!("Trade Recorded: {} bought {} kWh from {}", buyer, amount_kwh, seller);
        Ok(())
        
    }
}

// --- DATA STRUCTURES ---

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = 8 + 8 + 8)]
    pub stats: Account<'info, ProtocolStats>,
    #[account(mut)]
    pub authority: Signer<'info>, // The deployer pays for the account creation
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct RecordTrade<'info> {
    #[account(mut)]
    pub stats: Account<'info, ProtocolStats>,
    pub oracle: Signer<'info>, // Your Django backend must sign this transaction
}

// State Account to hold total estate data
#[account]
pub struct ProtocolStats {
    pub total_trades: u64,
    pub total_kwh_traded: u64,
}

// The Event logged to the blockchain
#[event]
pub struct TradeEvent {
    pub buyer: String,
    pub seller: String,
    pub amount_kwh: u64,
    pub price_kes: u64,
    pub timestamp: i64,
}