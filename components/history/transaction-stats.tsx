"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, TrendingUp, Activity } from "lucide-react"

const stats = [
  {
    title: "Total Sold",
    value: "142.8",
    unit: "eKWh",
    change: "+12.5%",
    trend: "up",
    icon: ArrowUpRight,
    color: "text-green-600",
  },
  {
    title: "Total Bought",
    value: "89.3",
    unit: "eKWh",
    change: "-8.2%",
    trend: "down",
    icon: ArrowDownRight,
    color: "text-blue-600",
  },
  {
    title: "Net Earnings",
    value: "4,230",
    unit: "KES",
    change: "+18.7%",
    trend: "up",
    icon: TrendingUp,
    color: "text-green-600",
  },
  {
    title: "Total Transactions",
    value: "47",
    unit: "trades",
    change: "+5",
    trend: "up",
    icon: Activity,
    color: "text-purple-600",
  },
]

export function TransactionStats() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
            <stat.icon className={`h-4 w-4 ${stat.color}`} />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">{stat.value}</div>
              <span className="text-sm text-muted-foreground">{stat.unit}</span>
            </div>
            <p className={`text-xs ${stat.trend === "up" ? "text-green-600" : "text-red-600"} mt-1`}>
              {stat.change} from last month
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
