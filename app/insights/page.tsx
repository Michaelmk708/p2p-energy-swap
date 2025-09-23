import { WeatherForecast } from "@/components/insights/weather-forecast"
import { AiRecommendations } from "@/components/insights/ai-recommendations"
import { EnergyPredictions } from "@/components/insights/energy-predictions"
import { OptimizationTips } from "@/components/insights/optimization-tips"

export default function InsightsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">AI Insights & Predictions</h1>
        <p className="text-muted-foreground text-pretty">
          Get intelligent recommendations and forecasts to optimize your energy production and trading.
        </p>
      </div>

      {/* AI Recommendations */}
      <AiRecommendations />

      {/* Predictions and Weather */}
      <div className="grid gap-6 lg:grid-cols-3">
        <EnergyPredictions />
        <WeatherForecast />
      </div>

      {/* Optimization Tips */}
      <OptimizationTips />
    </div>
  )
}
