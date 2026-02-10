// src/pages/Profile.tsx
import { useEffect, useMemo, useState } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Mail, Phone, MapPin, Save, LogOut, Zap, Award, LocateFixed } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { useUser } from "@/contexts/UserContext";
import useGeolocation from "@/hooks/useGeolocation";

type FormState = {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  location: string;
};

export default function Profile() {
  const navigate = useNavigate();
  const { user, logout } = useUser();
  const geo = useGeolocation();

  // Seed form with user values (keep UI responsive if user is not loaded yet)
  const [formData, setFormData] = useState<FormState>({
    // If backend provides a single `name` field, prefer that and attempt to split into first/last
    first_name: user?.first_name || (user?.name ? user.name.split(" ").slice(0, -1).join(" ") : "") || "",
    last_name: user?.last_name || (user?.name ? user.name.split(" ").slice(-1).join(" ") : "") || "",
    email: user?.email || "",
    phone: "",
    location: "",
  });

  // If user loads later, hydrate the form once (optional)
  useMemo(() => {
    if (user && !formData.first_name && !formData.last_name && !formData.email) {
      setFormData((prev) => ({
        ...prev,
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Seed location from cached geolocation city if present
  useEffect(() => {
    if (!formData.location) {
      try {
        const raw = localStorage.getItem('geo');
        if (raw) {
          const { city } = JSON.parse(raw);
          if (city) setFormData((p) => ({ ...p, location: city }));
        }
      } catch {}
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If user clicks "Use my location" and a city resolves, auto-fill the input if empty
  useEffect(() => {
    if (geo.city && !formData.location) {
      setFormData((p) => ({ ...p, location: geo.city || p.location }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geo.city]);

  // Prefer backend-provided full name (`user.name`) if present, otherwise fall back to first/last or username
  const displayFullName =
    user?.name || [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username || "User";

  const initials = (displayFullName || "U U")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const handleSave = () => {
    // TODO: Wire to backend /api/me/ PATCH later
    toast.success("Profile updated locally (wire to backend to persist).");
  };

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/auth", { replace: true });
  };

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Profile</h1>
          <p className="text-muted-foreground">Manage your account settings</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Overview */}
          <Card className="lg:col-span-1">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <Avatar className="h-24 w-24">
                  <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-2xl font-bold text-foreground">{displayFullName}</h2>
                  <p className="text-muted-foreground">@{(user?.username || "user").toLowerCase()}_solar</p>
                </div>

                <div className="w-full space-y-2 pt-4">
                  <div className="flex justify-between items-center p-3 rounded-lg bg-muted">
                    <span className="text-sm text-muted-foreground">Member Since</span>
                    <span className="font-medium text-foreground">Jan 2025</span>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-muted">
                    <span className="text-sm text-muted-foreground flex items-center gap-1">
                      <Zap className="h-3 w-3" />
                      Total Trades
                    </span>
                    <span className="font-medium text-foreground">127</span>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-primary/10">
                    <span className="text-sm text-primary flex items-center gap-1">
                      <Award className="h-3 w-3" />
                      Rating
                    </span>
                    <span className="font-bold text-primary">⭐ 4.9</span>
                  </div>
                </div>

                <Button variant="outline" className="w-full" onClick={handleLogout}>
                  <LogOutIcon />
                  Log Out
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Settings */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Update your personal details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Field
                  id="first_name"
                  label="First Name"
                  value={formData.first_name}
                  onChange={(v) => setFormData({ ...formData, first_name: v })}
                />
                <Field
                  id="last_name"
                  label="Last Name"
                  value={formData.last_name}
                  onChange={(v) => setFormData({ ...formData, last_name: v })}
                />
              </div>

              <Field
                id="email"
                label="Email"
                icon={<Mail className="h-4 w-4" />}
                type="email"
                value={formData.email}
                onChange={(v) => setFormData({ ...formData, email: v })}
              />
              <Field
                id="phone"
                label="Phone Number"
                icon={<Phone className="h-4 w-4" />}
                type="tel"
                value={formData.phone}
                onChange={(v) => setFormData({ ...formData, phone: v })}
              />
              <Field
                id="location"
                label="Location"
                icon={<MapPin className="h-4 w-4" />}
                value={formData.location}
                onChange={(v) => setFormData({ ...formData, location: v })}
              />
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    geo.refresh();
                  }}
                  disabled={geo.loading}
                >
                  <LocateFixed className="mr-2 h-4 w-4" />
                  Use my location
                </Button>
                {geo.coords && (
                  <span className="text-sm text-muted-foreground">
                    {geo.city || 'Detected location'} ({geo.coords.lat}, {geo.coords.lon})
                  </span>
                )}
              </div>

              {/* When geolocation city resolves, fill the input */}
              {geo.city && !formData.location && (
                <div>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setFormData((p) => ({ ...p, location: geo.city || p.location }))}
                  >
                    Fill with detected city: {geo.city}
                  </Button>
                </div>
              )}

              <Button variant="energy" onClick={handleSave} size="lg">
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Energy System Info (static demo) */}
        <Card>
          <CardHeader>
            <CardTitle>Energy System Configuration</CardTitle>
            <CardDescription>Your renewable energy setup</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard title="Solar Panels" value="5.2 kW" />
              <StatCard title="Battery Storage" value="10 kWh" accent />
              <StatusCard />
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

function Field({
  id,
  label,
  value,
  onChange,
  type = "text",
  icon,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="flex items-center gap-2">
        {icon}
        {label}
      </Label>
      <Input id={id} type={type} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function StatCard({ title, value, accent = false }: { title: string; value: string; accent?: boolean }) {
  return (
    <div className="p-4 rounded-lg border border-border">
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-2 rounded-lg ${accent ? "bg-accent/10" : "bg-primary/10"}`}>
          <Zap className={`h-4 w-4 ${accent ? "text-accent" : "text-primary"}`} />
        </div>
        <span className="font-medium text-foreground">{title}</span>
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground">Installed capacity</p>
    </div>
  );
}

function StatusCard() {
  return (
    <div className="p-4 rounded-lg border border-border">
      <div className="flex items-center gap-2 mb-2">
        <div className="p-2 rounded-lg bg-primary/10">
          <Award className="h-4 w-4 text-primary" />
        </div>
        <span className="font-medium text-foreground">Status</span>
      </div>
      <Badge variant="secondary" className="bg-primary/10 text-primary">
        Active & Connected
      </Badge>
    </div>
  );
}

function LogOutIcon() {
  return <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="none"><path d="M9 21H5a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h4" stroke="currentColor" strokeWidth="2"/><path d="M16 17l5-5-5-5" stroke="currentColor" strokeWidth="2"/><path d="M21 12H9" stroke="currentColor" strokeWidth="2"/></svg>;
}
