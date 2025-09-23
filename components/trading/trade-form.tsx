"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { ArrowUpRight, ArrowDownRight, Calculator } from "lucide-react"

export function TradeForm() {
  const [sellAmount, setSellAmount] = useState("")
  const [sellPrice, setSellPrice] = useState("")
  const [buyAmount, setBuyAmount] = useState("")
  const [buyPrice, setBuyPrice] = useState("")

  const calculateTotal = (amount: string, price: string) => {
    const amt = Number.parseFloat(amount) || 0
    const prc = Number.parseFloat(price) || 0
    return (amt * prc).toFixed(2)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-5 w-5 text-primary" />
          Place Order
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="sell" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="sell" className="flex items-center gap-2">
              <ArrowUpRight className="h-4 w-4" />
              Sell Energy
            </TabsTrigger>
            <TabsTrigger value="buy" className="flex items-center gap-2">
              <ArrowDownRight className="h-4 w-4" />
              Buy Energy
            </TabsTrigger>
          </TabsList>

          <TabsContent value="sell" className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="sell-amount">Amount (eKWh)</Label>
              <Input
                id="sell-amount"
                type="number"
                placeholder="0.00"
                value={sellAmount}
                onChange={(e) => setSellAmount(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Available: 24.7 eKWh</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="sell-price">Price per eKWh (KES)</Label>
              <Input
                id="sell-price"
                type="number"
                placeholder="50.00"
                value={sellPrice}
                onChange={(e) => setSellPrice(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="sell-type">Order Type</Label>
              <Select defaultValue="market">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="market">Market Order</SelectItem>
                  <SelectItem value="limit">Limit Order</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Value:</span>
                <span className="font-medium">KES {calculateTotal(sellAmount, sellPrice)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Platform Fee (2%):</span>
                <span className="font-medium">
                  KES {(Number.parseFloat(calculateTotal(sellAmount, sellPrice)) * 0.02).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-sm font-medium">
                <span>You'll Receive:</span>
                <span>KES {(Number.parseFloat(calculateTotal(sellAmount, sellPrice)) * 0.98).toFixed(2)}</span>
              </div>
            </div>

            <Button className="w-full" size="lg">
              Place Sell Order
            </Button>
          </TabsContent>

          <TabsContent value="buy" className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="buy-amount">Amount (eKWh)</Label>
              <Input
                id="buy-amount"
                type="number"
                placeholder="0.00"
                value={buyAmount}
                onChange={(e) => setBuyAmount(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="buy-price">Max Price per eKWh (KES)</Label>
              <Input
                id="buy-price"
                type="number"
                placeholder="50.00"
                value={buyPrice}
                onChange={(e) => setBuyPrice(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="buy-type">Order Type</Label>
              <Select defaultValue="market">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="market">Market Order</SelectItem>
                  <SelectItem value="limit">Limit Order</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Cost:</span>
                <span className="font-medium">KES {calculateTotal(buyAmount, buyPrice)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Platform Fee (2%):</span>
                <span className="font-medium">
                  KES {(Number.parseFloat(calculateTotal(buyAmount, buyPrice)) * 0.02).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">M-Pesa Balance:</span>
                <span className="font-medium">KES 3,450</span>
              </div>
            </div>

            <Button
              className="w-full bg-transparent"
              size="lg"
              variant="outline"
              disabled={Number.parseFloat(calculateTotal(buyAmount, buyPrice)) > 3450}
            >
              Place Buy Order
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
