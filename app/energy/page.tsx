"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Zap, Home, Battery, Sun, Activity, TrendingUp, TrendingDown, Power, Gauge } from "lucide-react"

const energyData = {
  currentProduction: 6.8,
  currentConsumption: 2.9,
  batteryLevel: 85,
  gridConnection: "connected",
  solarEfficiency: 92,
  dailyProduction: 45.2,
  dailyConsumption: 28.7,
  surplus: 16.5,
}

export default function EnergyPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Energy Monitor</h1>
        <p className="text-muted-foreground text-pretty">
          Real-time monitoring of your solar energy production, consumption, and system status.
        </p>
      </div>

      {/* Real-time Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Solar Production</CardTitle>
            <Sun className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{energyData.currentProduction} kWh</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% from last hour
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Home Consumption</CardTitle>
            <Home className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{energyData.currentConsumption} kWh</div>
            <p className="text-xs text-muted-foreground">
              <TrendingDown className="inline h-3 w-3 mr-1" />
              -5% from last hour
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Battery Level</CardTitle>
            <Battery className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{energyData.batteryLevel}%</div>
            <Progress value={energyData.batteryLevel} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Grid Status</CardTitle>
            <Power className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Connected
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-2">Stable connection</p>
          </CardContent>
        </Card>
      </div>

      {/* System Performance */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="h-5 w-5 text-primary" />
              System Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Solar Panel Efficiency</span>
                <span className="font-medium">{energyData.solarEfficiency}%</span>
              </div>
              <Progress value={energyData.solarEfficiency} className="h-2" />
            </div>

            <Separator />

            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-green-600">{energyData.dailyProduction}</p>
                <p className="text-xs text-muted-foreground">Daily Production (kWh)</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">{energyData.dailyConsumption}</p>
                <p className="text-xs text-muted-foreground">Daily Consumption (kWh)</p>
              </div>
            </div>

            <Separator />

            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{energyData.surplus}</p>
              <p className="text-xs text-muted-foreground">Daily Surplus (kWh)</p>
              <Badge
                variant="default"
                className="mt-2 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
              >
                Available for Trading
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Sell Surplus Energy
            </Button>

            <Button variant="outline" className="w-full flex items-center gap-2 bg-transparent">
              <Battery className="h-4 w-4" />
              Charge Battery
            </Button>

            <Button variant="outline" className="w-full flex items-center gap-2 bg-transparent">
              <Power className="h-4 w-4" />
              Grid Settings
            </Button>

            <Separator />

            <div className="space-y-2">
              <h4 className="text-sm font-medium">System Alerts</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2 p-2 rounded-lg bg-green-50 dark:bg-green-950">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-xs text-green-700 dark:text-green-300">
                    High production detected - Consider selling surplus
                  </span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50 dark:bg-blue-950">
                  <div className="h-2 w-2 rounded-full bg-blue-500" />
                  <span className="text-xs text-blue-700 dark:text-blue-300">Battery at optimal level</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
