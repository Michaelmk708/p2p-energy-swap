"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"

const sellOrders = [
  { id: 1, price: 52, amount: 15.5, seller: "House #23", distance: "0.2km" },
  { id: 2, price: 51, amount: 8.2, seller: "House #45", distance: "0.5km" },
  { id: 3, price: 50, amount: 22.1, seller: "House #67", distance: "0.8km" },
]

const buyOrders = [
  { id: 4, price: 49, amount: 12.3, buyer: "House #12", distance: "0.3km" },
  { id: 5, price: 48, amount: 18.7, buyer: "House #89", distance: "0.6km" },
  { id: 6, price: 47, amount: 9.4, buyer: "House #34", distance: "1.1km" },
]

export function OrderBook() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Order Book</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sell Orders */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <ArrowUpRight className="h-4 w-4 text-red-500" />
            <h3 className="font-medium text-sm">Sell Orders</h3>
            <Badge variant="outline" className="text-xs">
              {sellOrders.length}
            </Badge>
          </div>
          <div className="space-y-2">
            {sellOrders.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between p-2 rounded border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">KES {order.price}</span>
                    <span className="text-xs text-muted-foreground">{order.distance}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{order.amount} eKWh</span>
                    <span className="text-xs text-muted-foreground">{order.seller}</span>
                  </div>
                </div>
                <Button size="sm" variant="outline" className="ml-2 h-7 text-xs bg-transparent">
                  Buy
                </Button>
              </div>
            ))}
          </div>
        </div>

        {/* Buy Orders */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <ArrowDownRight className="h-4 w-4 text-green-500" />
            <h3 className="font-medium text-sm">Buy Orders</h3>
            <Badge variant="outline" className="text-xs">
              {buyOrders.length}
            </Badge>
          </div>
          <div className="space-y-2">
            {buyOrders.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between p-2 rounded border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">KES {order.price}</span>
                    <span className="text-xs text-muted-foreground">{order.distance}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{order.amount} eKWh</span>
                    <span className="text-xs text-muted-foreground">{order.buyer}</span>
                  </div>
                </div>
                <Button size="sm" className="ml-2 h-7 text-xs">
                  Sell
                </Button>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
