"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Smartphone, RefreshCw, Plus, ArrowUpRight } from "lucide-react"

export function MpesaBalance() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Smartphone className="h-5 w-5 text-green-600" />
          M-Pesa Wallet
        </CardTitle>
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          Connected
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center space-y-2">
          <p className="text-sm text-muted-foreground">Available Balance</p>
          <p className="text-3xl font-bold text-foreground">KES 3,450.00</p>
          <p className="text-xs text-muted-foreground">Last updated: 2 minutes ago</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Button className="flex items-center gap-2" size="sm">
            <Plus className="h-4 w-4" />
            Top Up
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2 bg-transparent">
            <ArrowUpRight className="h-4 w-4" />
            Withdraw
          </Button>
        </div>

        <div className="flex items-center justify-center pt-2">
          <Button variant="ghost" size="sm" className="flex items-center gap-2 text-muted-foreground">
            <RefreshCw className="h-4 w-4" />
            Refresh Balance
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
