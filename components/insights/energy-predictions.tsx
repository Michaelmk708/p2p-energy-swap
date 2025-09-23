"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart } from "recharts"
import { TrendingUp } from "lucide-react"

const predictionData = [
  { time: "6 AM", actual: 0.5, predicted: 0.8, demand: 2.1 },
  { time: "9 AM", actual: 4.2, predicted: 4.5, demand: 2.8 },
  { time: "12 PM", actual: 8.1, predicted: 8.3, demand: 3.1 },
  { time: "3 PM", actual: 6.8, predicted: 7.2, demand: 2.9 },
  { time: "6 PM", actual: null, predicted: 3.2, demand: 4.5 },
  { time: "9 PM", actual: null, predicted: 0.5, demand: 3.8 },
  { time: "12 AM", actual: null, predicted: 0, demand: 2.2 },
]

export function EnergyPredictions() {
  return (
    <Card className="col-span-1 md:col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-500" />
          Energy Production Predictions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={predictionData}>
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
            <Line
              type="monotone"
              dataKey="actual"
              stroke="hsl(var(--chart-1))"
              strokeWidth={2}
              dot={{ fill: "hsl(var(--chart-1))", strokeWidth: 2, r: 4 }}
              name="Actual Production"
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="hsl(var(--chart-2))"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 4 }}
              name="AI Prediction"
            />
            <Line
              type="monotone"
              dataKey="demand"
              stroke="hsl(var(--chart-3))"
              strokeWidth={2}
              dot={{ fill: "hsl(var(--chart-3))", strokeWidth: 2, r: 4 }}
              name="Local Demand"
            />
          </LineChart>
        </ResponsiveContainer>
        <div className="flex items-center justify-center gap-6 mt-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-chart-1"></div>
            <span>Actual Production</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-chart-2 border-2 border-dashed border-chart-2"></div>
            <span>AI Prediction</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-chart-3"></div>
            <span>Local Demand</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
