"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Zap, Settings } from "lucide-react"

export function EnergySystemSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Energy System Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Solar Panel Configuration */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Solar Panel Setup</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="panelCapacity">Total Capacity (kW)</Label>
              <Input id="panelCapacity" type="number" defaultValue="5.5" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="panelType">Panel Type</Label>
              <Select defaultValue="monocrystalline">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monocrystalline">Monocrystalline</SelectItem>
                  <SelectItem value="polycrystalline">Polycrystalline</SelectItem>
                  <SelectItem value="thin-film">Thin Film</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="panelAngle">Panel Angle (degrees)</Label>
              <Input id="panelAngle" type="number" defaultValue="30" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="panelOrientation">Orientation</Label>
              <Select defaultValue="south">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="north">North</SelectItem>
                  <SelectItem value="south">South</SelectItem>
                  <SelectItem value="east">East</SelectItem>
                  <SelectItem value="west">West</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        {/* Battery Storage */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Battery Storage</h3>
            <Switch defaultChecked />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="batteryCapacity">Battery Capacity (kWh)</Label>
              <Input id="batteryCapacity" type="number" defaultValue="10" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="batteryType">Battery Type</Label>
              <Select defaultValue="lithium-ion">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="lithium-ion">Lithium-ion</SelectItem>
                  <SelectItem value="lead-acid">Lead Acid</SelectItem>
                  <SelectItem value="saltwater">Saltwater</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        {/* Smart Meter */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Smart Meter Configuration</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="meterModel">Meter Model</Label>
              <Input id="meterModel" defaultValue="ESP32-Energy-Monitor" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="meterFirmware">Firmware Version</Label>
              <Input id="meterFirmware" defaultValue="v2.1.3" />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Update Configuration
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
