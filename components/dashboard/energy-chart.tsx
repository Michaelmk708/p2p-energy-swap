"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts"

const energyData = [
  { time: "00:00", production: 0, consumption: 2.1, surplus: -2.1 },
  { time: "06:00", production: 1.2, consumption: 3.2, surplus: -2.0 },
  { time: "09:00", production: 4.5, consumption: 2.8, surplus: 1.7 },
  { time: "12:00", production: 8.2, consumption: 3.1, surplus: 5.1 },
  { time: "15:00", production: 6.8, consumption: 2.9, surplus: 3.9 },
  { time: "18:00", production: 3.2, consumption: 4.5, surplus: -1.3 },
  { time: "21:00", production: 0.5, consumption: 3.8, surplus: -3.3 },
  { time: "24:00", production: 0, consumption: 2.2, surplus: -2.2 },
]

export function EnergyChart() {
  return (
    <Card className="col-span-1 md:col-span-2">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Energy Flow (24h)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={energyData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="time" className="text-xs fill-muted-foreground" />
            <YAxis
              className="text-xs fill-muted-foreground"
              label={{ value: "kWh", angle: -90, position: "insideLeft" }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--card-foreground))",
              }}
            />
            <Area
              type="monotone"
              dataKey="production"
              stackId="1"
              stroke="hsl(var(--chart-1))"
              fill="hsl(var(--chart-1))"
              fillOpacity={0.6}
              name="Production"
            />
            <Area
              type="monotone"
              dataKey="consumption"
              stackId="2"
              stroke="hsl(var(--chart-2))"
              fill="hsl(var(--chart-2))"
              fillOpacity={0.6}
              name="Consumption"
            />
            <Line
              type="monotone"
              dataKey="surplus"
              stroke="hsl(var(--chart-5))"
              strokeWidth={2}
              dot={{ fill: "hsl(var(--chart-5))", strokeWidth: 2, r: 4 }}
              name="Net Surplus"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
