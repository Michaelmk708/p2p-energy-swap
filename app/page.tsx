import { EnergyStatsCard } from "@/components/dashboard/energy-stats-card"
import { EnergyChart } from "@/components/dashboard/energy-chart"
import { BalanceOverview } from "@/components/dashboard/balance-overview"
import { RecentTransactions } from "@/components/dashboard/recent-transactions"
import { Zap, Home, TrendingUp, Users } from "lucide-react"

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Welcome back, John!</h1>
        <p className="text-muted-foreground text-pretty">
          Monitor your energy production, manage trades, and optimize your renewable energy usage.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <EnergyStatsCard
          title="Current Production"
          value="6.8"
          unit="kWh"
          change={12}
          trend="up"
          status="surplus"
          icon={<Zap className="h-5 w-5 text-primary" />}
        />
        <EnergyStatsCard
          title="Home Consumption"
          value="2.9"
          unit="kWh"
          change={-5}
          trend="down"
          icon={<Home className="h-5 w-5 text-blue-500" />}
        />
        <EnergyStatsCard
          title="Today's Earnings"
          value="1,240"
          unit="KES"
          change={18}
          trend="up"
          icon={<TrendingUp className="h-5 w-5 text-green-500" />}
        />
        <EnergyStatsCard
          title="Active Trades"
          value="7"
          unit="trades"
          change={2}
          trend="up"
          icon={<Users className="h-5 w-5 text-purple-500" />}
        />
      </div>

      {/* Charts and Details */}
      <div className="grid gap-6 md:grid-cols-3">
        <EnergyChart />
        <div className="space-y-6">
          <BalanceOverview />
          <RecentTransactions />
        </div>
      </div>
    </div>
  )
}
