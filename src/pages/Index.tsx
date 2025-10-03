import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Sun, Battery, TrendingUp, Leaf, ArrowRight, Users, ShieldCheck } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 energy-gradient opacity-10" />
        <div className="container mx-auto px-4 py-20 relative">
          <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/20 bg-primary/5">
              <Leaf className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">Renewable Energy Marketplace</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-foreground leading-tight">
              Trade Solar Energy
              <span className="block energy-gradient bg-clip-text text-transparent">
                With Your Community
              </span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Join Kenya's first peer-to-peer energy trading platform. Buy and sell excess solar energy tokens, reduce costs, and build a sustainable future together.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <Link to="/auth">
                <Button variant="energy" size="lg" className="text-lg px-8">
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button variant="eco" size="lg" className="text-lg px-8">
                  View Demo
                </Button>
              </Link>
            </div>

            <div className="grid grid-cols-3 gap-8 pt-12">
              <div>
                <p className="text-3xl font-bold text-foreground">1,245+</p>
                <p className="text-sm text-muted-foreground">Active Users</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-foreground">50k+</p>
                <p className="text-sm text-muted-foreground">Tokens Traded</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-foreground">35%</p>
                <p className="text-sm text-muted-foreground">Cost Savings</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Why Choose P2P Energy Swap?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Harness the power of community-driven renewable energy trading
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-primary/20 hover:shadow-lg transition-smooth animate-scale-in">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 w-fit mb-2">
                  <Sun className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Solar-Powered</CardTitle>
                <CardDescription>
                  Trade excess solar energy from your rooftop panels
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-primary/20 hover:shadow-lg transition-smooth animate-scale-in" style={{ animationDelay: "0.1s" }}>
              <CardHeader>
                <div className="p-3 rounded-lg bg-accent/10 w-fit mb-2">
                  <TrendingUp className="h-6 w-6 text-accent" />
                </div>
                <CardTitle>Real-Time Market</CardTitle>
                <CardDescription>
                  Dynamic pricing based on supply and demand
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-primary/20 hover:shadow-lg transition-smooth animate-scale-in" style={{ animationDelay: "0.2s" }}>
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 w-fit mb-2">
                  <Battery className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>AI Predictions</CardTitle>
                <CardDescription>
                  Smart forecasts for usage and production
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-primary/20 hover:shadow-lg transition-smooth animate-scale-in" style={{ animationDelay: "0.3s" }}>
              <CardHeader>
                <div className="p-3 rounded-lg bg-accent/10 w-fit mb-2">
                  <ShieldCheck className="h-6 w-6 text-accent" />
                </div>
                <CardTitle>Secure Trading</CardTitle>
                <CardDescription>
                  Safe and transparent energy transactions
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              How It Works
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Start trading renewable energy in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full energy-gradient flex items-center justify-center text-white text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-foreground">Connect Your System</h3>
              <p className="text-muted-foreground">
                Link your solar panels and smart meter to track energy production
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full energy-gradient flex items-center justify-center text-white text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-foreground">Trade Energy Tokens</h3>
              <p className="text-muted-foreground">
                Buy tokens when you need energy, sell when you have surplus
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full energy-gradient flex items-center justify-center text-white text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-foreground">Save & Earn</h3>
              <p className="text-muted-foreground">
                Reduce electricity costs and earn from your excess solar power
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 solar-gradient opacity-10" />
        <div className="container mx-auto px-4 relative">
          <Card className="max-w-4xl mx-auto border-primary/20 glow-green">
            <CardContent className="p-12 text-center space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10">
                <Users className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium text-primary">Join 1,000+ Energy Traders</span>
              </div>
              
              <h2 className="text-3xl md:text-4xl font-bold text-foreground">
                Ready to Start Trading Renewable Energy?
              </h2>
              
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Create your free account today and become part of Kenya's sustainable energy revolution
              </p>

              <Link to="/auth">
                <Button variant="energy" size="lg" className="text-lg px-8">
                  Create Free Account
                  <Zap className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg energy-gradient">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-foreground">P2P Energy Swap</p>
                <p className="text-xs text-muted-foreground">Powered by renewable energy</p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Leaf className="h-4 w-4 text-primary" />
              <p>Empowering communities through renewable energy</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
