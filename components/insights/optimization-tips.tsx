"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Lightbulb, Zap, DollarSign, Leaf, ExternalLink } from "lucide-react"

const tips = [
  {
    id: 1,
    category: "efficiency",
    title: "Panel Angle Optimization",
    description: "Adjusting your solar panels by 15° could increase production by 12% during winter months.",
    impact: "High",
    savings: "KES 340/month",
    icon: Zap,
  },
  {
    id: 2,
    category: "trading",
    title: "Peak Hour Trading",
    description: "Selling during 2-4 PM peak hours can increase your earnings by 25% compared to off-peak rates.",
    impact: "Medium",
    savings: "KES 180/month",
    icon: DollarSign,
  },
  {
    id: 3,
    category: "sustainability",
    title: "Battery Storage Investment",
    description: "Adding 10kWh battery storage could reduce grid dependency by 60% and increase trading flexibility.",
    impact: "High",
    savings: "KES 520/month",
    icon: Leaf,
  },
]

export function OptimizationTips() {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case "efficiency":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "trading":
        return "bg-green-100 text-green-800 border-green-200"
      default:
        return "bg-purple-100 text-purple-800 border-purple-200"
    }
  }

  const getImpactColor = (impact: string) => {
    return impact === "High"
      ? "bg-red-100 text-red-800 border-red-200"
      : "bg-yellow-100 text-yellow-800 border-yellow-200"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Optimization Tips
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tips.map((tip) => (
            <div key={tip.id} className="p-4 rounded-lg border border-border bg-card">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <tip.icon className="h-4 w-4 text-primary" />
                  <h3 className="font-medium text-sm">{tip.title}</h3>
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline" className={getCategoryColor(tip.category)}>
                    {tip.category}
                  </Badge>
                  <Badge variant="outline" className={getImpactColor(tip.impact)}>
                    {tip.impact}
                  </Badge>
                </div>
              </div>

              <p className="text-sm text-muted-foreground mb-3">{tip.description}</p>

              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <span className="text-muted-foreground">Potential savings: </span>
                  <span className="font-medium text-green-600">{tip.savings}</span>
                </div>
                <Button size="sm" variant="outline" className="h-7 text-xs flex items-center gap-1 bg-transparent">
                  Learn More
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
