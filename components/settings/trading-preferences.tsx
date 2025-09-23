"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Slider } from "@/components/ui/slider"
import { ArrowLeftRight } from "lucide-react"

export function TradingPreferences() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowLeftRight className="h-5 w-5" />
          Trading Preferences
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Auto Trading */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">Auto Trading</h3>
              <p className="text-xs text-muted-foreground">Automatically sell surplus energy when available</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="space-y-4 pl-4 border-l-2 border-muted">
            <div className="space-y-2">
              <Label htmlFor="minPrice">Minimum Selling Price (KES per eKWh)</Label>
              <Input id="minPrice" type="number" defaultValue="45" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxPrice">Maximum Buying Price (KES per eKWh)</Label>
              <Input id="maxPrice" type="number" defaultValue="55" />
            </div>
          </div>
        </div>

        <Separator />

        {/* Trading Limits */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Trading Limits</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Maximum Daily Trading Volume</Label>
              <div className="px-3">
                <Slider defaultValue={[75]} max={100} step={5} className="w-full" />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0 eKWh</span>
                <span>75 eKWh</span>
                <span>100 eKWh</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Reserve Energy Buffer (%)</Label>
              <div className="px-3">
                <Slider defaultValue={[20]} max={50} step={5} className="w-full" />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0%</span>
                <span>20%</span>
                <span>50%</span>
              </div>
            </div>
          </div>
        </div>

        <Separator />

        {/* Notifications */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Trading Notifications</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="tradeComplete" className="text-sm font-normal">
                Trade Completion
              </Label>
              <Switch id="tradeComplete" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="priceAlerts" className="text-sm font-normal">
                Price Alerts
              </Label>
              <Switch id="priceAlerts" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="lowBalance" className="text-sm font-normal">
                Low Balance Warnings
              </Label>
              <Switch id="lowBalance" defaultChecked />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button>Save Preferences</Button>
        </div>
      </CardContent>
    </Card>
  )
}
