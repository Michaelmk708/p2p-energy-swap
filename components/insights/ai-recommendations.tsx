"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Brain, TrendingUp, AlertTriangle, Lightbulb, Clock } from "lucide-react"

const recommendations = [
  {
    id: 1,
    type: "sell",
    priority: "high",
    title: "Optimal Selling Window",
    description: "Peak demand expected between 2-4 PM today. Consider selling 8-12 eKWh at KES 55-58.",
    confidence: 92,
    timeframe: "Next 2 hours",
    icon: TrendingUp,
  },
  {
    id: 2,
    type: "buy",
    priority: "medium",
    title: "Price Drop Prediction",
    description: "Energy prices likely to drop 15% tomorrow morning due to high solar production forecast.",
    confidence: 78,
    timeframe: "Tomorrow 8-10 AM",
    icon: Lightbulb,
  },
  {
    id: 3,
    type: "alert",
    priority: "high",
    title: "Maintenance Alert",
    description: "Your solar panel efficiency has decreased by 8%. Consider cleaning or inspection.",
    confidence: 95,
    timeframe: "This week",
    icon: AlertTriangle,
  },
]

export function AiRecommendations() {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      default:
        return "bg-blue-100 text-blue-800 border-blue-200"
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "sell":
        return "text-green-600"
      case "buy":
        return "text-blue-600"
      default:
        return "text-orange-600"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-500" />
          AI Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div key={rec.id} className="p-4 rounded-lg border border-border bg-card">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <rec.icon className={`h-4 w-4 ${getTypeColor(rec.type)}`} />
                  <h3 className="font-medium text-sm">{rec.title}</h3>
                </div>
                <Badge variant="outline" className={getPriorityColor(rec.priority)}>
                  {rec.priority}
                </Badge>
              </div>

              <p className="text-sm text-muted-foreground mb-3">{rec.description}</p>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {rec.timeframe}
                  </div>
                  <span>Confidence: {rec.confidence}%</span>
                </div>
                <Button size="sm" variant="outline" className="h-7 text-xs bg-transparent">
                  Act Now
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
