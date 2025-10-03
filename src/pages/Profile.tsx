import { useState } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User, Mail, Phone, MapPin, Save, LogOut, Zap, Award } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { useUser } from "@/contexts/UserContext";

export default function Profile() {
  const navigate = useNavigate();
  const { profile, updateProfile } = useUser();
  
  const [formData, setFormData] = useState(profile);

  const handleSave = () => {
    updateProfile(formData);
    toast.success("Profile updated successfully");
  };

  const handleLogout = () => {
    toast.success("Logged out successfully");
    navigate("/");
  };

  const getInitials = () => {
    return `${formData.firstName[0]}${formData.lastName[0]}`.toUpperCase();
  };

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Profile</h1>
          <p className="text-muted-foreground">Manage your account settings</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Overview */}
          <Card className="lg:col-span-1">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <Avatar className="h-24 w-24">
                  <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                    {getInitials()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-2xl font-bold text-foreground">{formData.firstName} {formData.lastName}</h2>
                  <p className="text-muted-foreground">@{formData.firstName.toLowerCase()}{formData.lastName.toLowerCase()}_solar</p>
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
                  <LogOut className="mr-2 h-4 w-4" />
                  Log Out
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Profile Settings */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Update your personal details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input 
                    id="firstName" 
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input 
                    id="lastName" 
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email
                </Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone" className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Phone Number
                </Label>
                <Input 
                  id="phone" 
                  type="tel" 
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </Label>
                <Input 
                  id="location" 
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>

              <Button variant="energy" onClick={handleSave} size="lg">
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Energy System Info */}
        <Card>
          <CardHeader>
            <CardTitle>Energy System Configuration</CardTitle>
            <CardDescription>Your renewable energy setup</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg border border-border">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Zap className="h-4 w-4 text-primary" />
                  </div>
                  <span className="font-medium text-foreground">Solar Panels</span>
                </div>
                <p className="text-2xl font-bold text-foreground">5.2 kW</p>
                <p className="text-xs text-muted-foreground">Installed capacity</p>
              </div>

              <div className="p-4 rounded-lg border border-border">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-accent/10">
                    <Zap className="h-4 w-4 text-accent" />
                  </div>
                  <span className="font-medium text-foreground">Battery Storage</span>
                </div>
                <p className="text-2xl font-bold text-foreground">10 kWh</p>
                <p className="text-xs text-muted-foreground">Storage capacity</p>
              </div>

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
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
