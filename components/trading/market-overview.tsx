"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Activity } from "lucide-react"

const marketData = {
  currentPrice: 50,
  change24h: 2.5,
  volume24h: 1247,
  totalSupply: 3420,
  totalDemand: 2890,
  activeTraders: 156,
}

export function MarketOverview() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          Market Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Current Price</p>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">KES {marketData.currentPrice}</span>
              <Badge variant={marketData.change24h > 0 ? "default" : "destructive"} className="flex items-center gap-1">
                {marketData.change24h > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {Math.abs(marketData.change24h)}%
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">per eKWh</p>
          </div>

          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">24h Volume</p>
            <span className="text-2xl font-bold">{marketData.volume24h}</span>
            <p className="text-xs text-muted-foreground">eKWh traded</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">Supply</p>
            <p className="text-lg font-semibold text-green-600">{marketData.totalSupply}</p>
            <p className="text-xs text-muted-foreground">eKWh</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">Demand</p>
            <p className="text-lg font-semibold text-blue-600">{marketData.totalDemand}</p>
            <p className="text-xs text-muted-foreground">eKWh</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">Traders</p>
            <p className="text-lg font-semibold text-purple-600">{marketData.activeTraders}</p>
            <p className="text-xs text-muted-foreground">active</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
