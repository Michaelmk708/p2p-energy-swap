import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Zap, Leaf, Sun } from "lucide-react";
import { toast } from "sonner";
import { useUser } from "@/contexts/UserContext";

export default function Auth() {
  const { login, register, user } = useUser();
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();

  // ✅ Only redirect if we truly have a user (hydrated from /me)
  if (user) {
    const from = (location.state as any)?.from?.pathname || "/dashboard";
    return <Navigate to={from} replace />;
  }

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const form = e.currentTarget;
      const email = (form.querySelector("#email") as HTMLInputElement).value.trim();
      const password = (form.querySelector("#password") as HTMLInputElement).value;
      await login(email, password);          // saves tokens + fetches /me
      toast.success("Welcome back!");
      window.location.replace("/dashboard"); // guarantee navigation
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const form = e.currentTarget;
      const fullName = (form.querySelector("#signup-name") as HTMLInputElement).value.trim();
      const [first_name = "", last_name = ""] = fullName.split(/\s+/, 2);
      const email = (form.querySelector("#signup-email") as HTMLInputElement).value.trim();
      const password = (form.querySelector("#signup-password") as HTMLInputElement).value;

      await register({
        email,
        password,
        username: email.split("@")[0],
        first_name,
        last_name,
        role: "consumer",
      });                                     // also auto-logins and fetches /me
      toast.success("Account created successfully!");
      window.location.replace("/dashboard");
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || "Signup failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left: Branding (no app header) */}
        <div className="hidden md:block space-y-6 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl energy-gradient">
              <Zap className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">P2P Energy Swap</h1>
              <p className="text-muted-foreground">Trade renewable energy tokens</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 rounded-lg eco-gradient">
              <Sun className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-foreground">Solar-Powered Trading</h3>
                <p className="text-sm text-muted-foreground">Buy and sell excess solar energy with your neighbors</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg eco-gradient">
              <Zap className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-foreground">Real-Time Marketplace</h3>
                <p className="text-sm text-muted-foreground">Set your own prices and trade energy tokens instantly</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg eco-gradient">
              <Leaf className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-foreground">Sustainable Future</h3>
                <p className="text-sm text-muted-foreground">Join the green energy revolution and reduce carbon footprint</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Forms */}
        <Card className="animate-scale-in">
          <CardHeader>
            <CardTitle>Welcome</CardTitle>
            <CardDescription>Sign in to your account or create a new one</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login">
              <TabsList className="grid w-full grid-cols-2 mb-4">
                <TabsTrigger value="login">Login</TabsTrigger>
                <TabsTrigger value="signup">Sign Up</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" placeholder="you@example.com" autoComplete="email" required disabled={isLoading} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input id="password" type="password" placeholder="••••••••" autoComplete="current-password" required disabled={isLoading} />
                  </div>
                  <Button type="submit" variant="energy" className="w-full" disabled={isLoading}>
                    {isLoading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-name">Full Name</Label>
                    <Input id="signup-name" type="text" placeholder="John Doe" autoComplete="name" required disabled={isLoading} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <Input id="signup-email" type="email" placeholder="you@example.com" autoComplete="email" required disabled={isLoading} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <Input id="signup-password" type="password" placeholder="••••••••" autoComplete="new-password" required disabled={isLoading} />
                  </div>
                  <Button type="submit" variant="energy" className="w-full" disabled={isLoading}>
                    {isLoading ? "Creating account..." : "Create Account"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
