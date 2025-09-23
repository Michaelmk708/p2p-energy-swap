"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Shield, Key, Smartphone, AlertTriangle } from "lucide-react"

export function SecuritySettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Security & Privacy
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Password Change */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Change Password</h3>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Current Password</Label>
              <Input id="currentPassword" type="password" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input id="newPassword" type="password" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input id="confirmPassword" type="password" />
            </div>
            <Button size="sm">Update Password</Button>
          </div>
        </div>

        <Separator />

        {/* Two-Factor Authentication */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">Two-Factor Authentication</h3>
              <p className="text-xs text-muted-foreground">Add an extra layer of security to your account</p>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              Enabled
            </Badge>
          </div>

          <div className="space-y-3 pl-4 border-l-2 border-muted">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Smartphone className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">SMS Authentication</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Key className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Authenticator App</span>
              </div>
              <Switch />
            </div>
          </div>
        </div>

        <Separator />

        {/* Blockchain Security */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Blockchain Security</h3>
          <div className="space-y-3">
            <div className="p-3 rounded-lg border border-border bg-muted/50">
              <div className="flex items-center gap-2 mb-2">
                <Key className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Wallet Address</span>
              </div>
              <p className="text-xs font-mono text-muted-foreground">0x1234...5678</p>
              <Button size="sm" variant="outline" className="mt-2 bg-transparent">
                View on Solana Explorer
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="requireConfirmation" className="text-sm font-normal">
                Require confirmation for large transactions
              </Label>
              <Switch id="requireConfirmation" defaultChecked />
            </div>
          </div>
        </div>

        <Separator />

        {/* Privacy Settings */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Privacy Settings</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="shareData" className="text-sm font-normal">
                Share anonymous usage data for AI improvements
              </Label>
              <Switch id="shareData" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="publicProfile" className="text-sm font-normal">
                Make trading profile visible to neighbors
              </Label>
              <Switch id="publicProfile" />
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="space-y-4 pt-4 border-t border-destructive/20">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-destructive" />
            <h3 className="text-sm font-medium text-destructive">Danger Zone</h3>
          </div>
          <div className="space-y-2">
            <Button variant="destructive" size="sm">
              Delete Account
            </Button>
            <p className="text-xs text-muted-foreground">
              This action cannot be undone. All your data will be permanently deleted.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
