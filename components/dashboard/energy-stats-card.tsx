"use client"

import type React from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Battery } from "lucide-react"

interface EnergyStatsCardProps {
  title: string
  value: string
  unit: string
  change: number
  trend: "up" | "down" | "neutral"
  icon: React.ReactNode
  status?: "surplus" | "deficit" | "balanced"
}

export function EnergyStatsCard({ title, value, unit, change, trend, icon, status }: EnergyStatsCardProps) {
  const getTrendIcon = () => {
    if (trend === "up") return <TrendingUp className="h-4 w-4 text-green-500" />
    if (trend === "down") return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Battery className="h-4 w-4 text-muted-foreground" />
  }

  const getStatusBadge = () => {
    if (!status) return null

    const statusConfig = {
      surplus: { label: "Surplus", className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" },
      deficit: { label: "Deficit", className: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" },
      balanced: { label: "Balanced", className: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" },
    }

    const config = statusConfig[status]
    return <Badge className={config.className}>{config.label}</Badge>
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div className="flex items-center gap-2">
          {getStatusBadge()}
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold text-foreground">{value}</div>
          <span className="text-sm text-muted-foreground">{unit}</span>
        </div>
        <div className="flex items-center gap-1 mt-2">
          {getTrendIcon()}
          <span
            className={`text-xs ${
              trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-muted-foreground"
            }`}
          >
            {change > 0 ? "+" : ""}
            {change}% from last hour
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
