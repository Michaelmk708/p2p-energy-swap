"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, ArrowDownRight, X, Clock } from "lucide-react"

const activeOrders = [
  {
    id: "ord_001",
    type: "sell",
    amount: 12.5,
    price: 52,
    total: 650,
    status: "active",
    timeLeft: "2h 15m",
    filled: 0,
  },
  {
    id: "ord_002",
    type: "buy",
    amount: 8.0,
    price: 48,
    total: 384,
    status: "partial",
    timeLeft: "4h 32m",
    filled: 3.2,
  },
  {
    id: "ord_003",
    type: "sell",
    amount: 15.8,
    price: 51,
    total: 805.8,
    status: "active",
    timeLeft: "1h 45m",
    filled: 0,
  },
]

export function ActiveOrders() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Active Orders</CardTitle>
        <Badge variant="outline">{activeOrders.length}</Badge>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activeOrders.map((order) => (
            <div key={order.id} className="p-3 rounded-lg border border-border bg-card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {order.type === "sell" ? (
                    <ArrowUpRight className="h-4 w-4 text-red-500" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-green-500" />
                  )}
                  <span className="font-medium text-sm capitalize">{order.type}</span>
                  <Badge variant={order.status === "active" ? "default" : "secondary"}>{order.status}</Badge>
                </div>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <X className="h-3 w-3" />
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <p className="text-muted-foreground">Amount</p>
                  <p className="font-medium">{order.amount} eKWh</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Price</p>
                  <p className="font-medium">KES {order.price}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Total</p>
                  <p className="font-medium">KES {order.total}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Filled</p>
                  <p className="font-medium">{order.filled} eKWh</p>
                </div>
              </div>

              <div className="flex items-center justify-between mt-2 pt-2 border-t border-border">
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {order.timeLeft} remaining
                </div>
                <div className="text-xs">
                  {order.filled > 0 && (
                    <span className="text-green-600">{((order.filled / order.amount) * 100).toFixed(1)}% filled</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
