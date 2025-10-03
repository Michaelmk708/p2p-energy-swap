import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Zap, 
  TrendingUp, 
  TrendingDown, 
  Battery, 
  Sun, 
  Wind,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles
} from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { useNavigate } from "react-router-dom";

// Dummy data
const energyUsageData = [
  { time: "00:00", usage: 2.1, production: 0 },
  { time: "04:00", usage: 1.8, production: 0 },
  { time: "08:00", usage: 3.2, production: 1.5 },
  { time: "12:00", usage: 2.8, production: 4.2 },
  { time: "16:00", usage: 3.5, production: 3.8 },
  { time: "20:00", usage: 4.1, production: 0.5 },
];

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Monitor your energy usage and trading activity</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Token Balance */}
          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Token Balance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">245</div>
              <div className="flex items-center gap-1 text-sm text-primary mt-1">
                <TrendingUp className="h-3 w-3" />
                <span>+12% this week</span>
              </div>
            </CardContent>
          </Card>

          {/* Energy Exported */}
          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowUpRight className="h-4 w-4 text-accent" />
                Energy Exported
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">142 kWh</div>
              <div className="flex items-center gap-1 text-sm text-accent mt-1">
                <Sun className="h-3 w-3" />
                <span>Solar surplus</span>
              </div>
            </CardContent>
          </Card>

          {/* Energy Consumed */}
          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowDownRight className="h-4 w-4 text-primary" />
                Energy Consumed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">89 kWh</div>
              <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                <Battery className="h-3 w-3" />
                <span>From grid & P2P</span>
              </div>
            </CardContent>
          </Card>

          {/* Savings */}
          <Card className="hover:shadow-lg transition-smooth">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" />
                Total Savings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">KES 3,240</div>
              <div className="flex items-center gap-1 text-sm text-primary mt-1">
                <span>vs. standard rates</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Energy Usage Graph */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Battery className="h-5 w-5 text-primary" />
              Energy Flow (24h)
            </CardTitle>
            <CardDescription>Your production vs. consumption today</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={energyUsageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="time" 
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  label={{ value: 'kWh', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="production" 
                  stroke="hsl(142 76% 36%)" 
                  strokeWidth={3}
                  name="Production"
                  dot={{ fill: 'hsl(142 76% 36%)', r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="hsl(180 75% 45%)" 
                  strokeWidth={3}
                  name="Consumption"
                  dot={{ fill: 'hsl(180 75% 45%)', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* AI Predictions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                AI Prediction: Tomorrow
              </CardTitle>
              <CardDescription>Smart forecast based on weather & history</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Expected Production</span>
                  <Badge variant="secondary">+15%</Badge>
                </div>
                <div className="text-2xl font-bold text-foreground">168 kWh</div>
                <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                  <Sun className="h-3 w-3" />
                  Sunny weather expected
                </p>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Expected Consumption</span>
                  <Badge variant="secondary">-5%</Badge>
                </div>
                <div className="text-2xl font-bold text-foreground">85 kWh</div>
                <p className="text-sm text-muted-foreground">Similar to today</p>
              </div>

              <div className="pt-4 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Estimated Surplus</span>
                  <span className="text-xl font-bold text-primary">83 kWh</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Consider listing tokens for sale
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Manage your energy trading</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                variant="energy" 
                className="w-full justify-start" 
                size="lg"
                onClick={() => navigate("/marketplace?tab=my-listings")}
              >
                <Zap className="mr-2 h-5 w-5" />
                List Tokens for Sale
              </Button>
              <Button 
                variant="eco" 
                className="w-full justify-start" 
                size="lg"
                onClick={() => navigate("/marketplace?tab=buy")}
              >
                <Sun className="mr-2 h-5 w-5" />
                Buy Energy Tokens
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start" 
                size="lg"
                onClick={() => navigate("/marketplace")}
              >
                <Wind className="mr-2 h-5 w-5" />
                View Market Trends
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
