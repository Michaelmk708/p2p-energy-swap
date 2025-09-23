import { ProfileSettings } from "@/components/settings/profile-settings"
import { EnergySystemSettings } from "@/components/settings/energy-system-settings"
import { TradingPreferences } from "@/components/settings/trading-preferences"
import { SecuritySettings } from "@/components/settings/security-settings"

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Settings</h1>
        <p className="text-muted-foreground text-pretty">
          Manage your account, energy system configuration, and trading preferences.
        </p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        <ProfileSettings />
        <EnergySystemSettings />
        <TradingPreferences />
        <SecuritySettings />
      </div>
    </div>
  )
}
