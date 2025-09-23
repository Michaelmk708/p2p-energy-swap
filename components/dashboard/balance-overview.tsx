"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Coins, Zap, ArrowUpRight, ArrowDownRight } from "lucide-react"

export function BalanceOverview() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="h-5 w-5 text-primary" />
          Account Balance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Energy Tokens */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-accent" />
              <span className="text-sm font-medium">Energy Tokens (eKWh)</span>
            </div>
            <span className="text-lg font-bold text-foreground">24.7</span>
          </div>
          <div className="text-xs text-muted-foreground">≈ KES 1,235 at current rate</div>
        </div>

        <Separator />

        {/* Fiat Balance */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">M-Pesa Balance</span>
            <span className="text-lg font-bold text-foreground">KES 3,450</span>
          </div>
          <div className="text-xs text-muted-foreground">Available for energy purchases</div>
        </div>

        <Separator />

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-2">
          <Button size="sm" className="flex items-center gap-1">
            <ArrowUpRight className="h-3 w-3" />
            Sell Energy
          </Button>
          <Button size="sm" variant="outline" className="flex items-center gap-1 bg-transparent">
            <ArrowDownRight className="h-3 w-3" />
            Buy Energy
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
