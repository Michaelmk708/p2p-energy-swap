"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Cloud, Sun, CloudRain, Wind } from "lucide-react"

const weatherData = [
  { day: "Today", condition: "sunny", temp: "28°C", production: "High", icon: Sun },
  { day: "Tomorrow", condition: "partly-cloudy", temp: "26°C", production: "Medium", icon: Cloud },
  { day: "Wed", condition: "rainy", temp: "22°C", production: "Low", icon: CloudRain },
  { day: "Thu", condition: "sunny", temp: "30°C", production: "High", icon: Sun },
  { day: "Fri", condition: "windy", temp: "25°C", production: "Medium", icon: Wind },
]

export function WeatherForecast() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sun className="h-5 w-5 text-yellow-500" />
          Weather & Production Forecast
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {weatherData.map((day, index) => (
            <div key={day.day} className="flex items-center justify-between p-3 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <day.icon className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium text-sm">{day.day}</p>
                  <p className="text-xs text-muted-foreground capitalize">{day.condition}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{day.temp}</span>
                <Badge
                  variant={
                    day.production === "High" ? "default" : day.production === "Medium" ? "secondary" : "outline"
                  }
                  className={
                    day.production === "High"
                      ? "bg-green-100 text-green-800 border-green-200"
                      : day.production === "Medium"
                        ? "bg-yellow-100 text-yellow-800 border-yellow-200"
                        : "bg-red-100 text-red-800 border-red-200"
                  }
                >
                  {day.production}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
