import { MarketOverview } from "@/components/trading/market-overview"
import { OrderBook } from "@/components/trading/order-book"
import { TradeForm } from "@/components/trading/trade-form"
import { ActiveOrders } from "@/components/trading/active-orders"

export default function TradingPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Energy Trading</h1>
        <p className="text-muted-foreground text-pretty">
          Buy and sell renewable energy tokens with your neighbors in real-time.
        </p>
      </div>

      {/* Market Overview */}
      <MarketOverview />

      {/* Trading Interface */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-6">
          <TradeForm />
          <ActiveOrders />
        </div>
        <div className="lg:col-span-2">
          <OrderBook />
        </div>
      </div>
    </div>
  )
}
