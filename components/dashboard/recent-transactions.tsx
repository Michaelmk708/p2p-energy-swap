"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, ArrowDownRight, Clock, ExternalLink } from "lucide-react"

const transactions = [
  {
    id: "tx_001",
    type: "sell",
    amount: "5.2 eKWh",
    value: "KES 260",
    buyer: "House #47",
    timestamp: "2 min ago",
    status: "completed",
  },
  {
    id: "tx_002",
    type: "buy",
    amount: "3.1 eKWh",
    value: "KES 155",
    seller: "House #23",
    timestamp: "15 min ago",
    status: "completed",
  },
  {
    id: "tx_003",
    type: "sell",
    amount: "8.7 eKWh",
    value: "KES 435",
    buyer: "House #12",
    timestamp: "1 hour ago",
    status: "pending",
  },
]

export function RecentTransactions() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold">Recent Transactions</CardTitle>
        <Button variant="ghost" size="sm" className="flex items-center gap-1">
          View All
          <ExternalLink className="h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {transactions.map((tx) => (
            <div key={tx.id} className="flex items-center justify-between p-3 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-full ${
                    tx.type === "sell" ? "bg-green-100 dark:bg-green-900" : "bg-blue-100 dark:bg-blue-900"
                  }`}
                >
                  {tx.type === "sell" ? (
                    <ArrowUpRight className="h-4 w-4 text-green-600 dark:text-green-400" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">
                      {tx.type === "sell" ? "Sold to" : "Bought from"} {tx.type === "sell" ? tx.buyer : tx.seller}
                    </span>
                    <Badge variant={tx.status === "completed" ? "default" : "secondary"}>{tx.status}</Badge>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {tx.timestamp}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-sm">{tx.amount}</div>
                <div className="text-xs text-muted-foreground">{tx.value}</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
