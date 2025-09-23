"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Smartphone, Plus, Settings } from "lucide-react"

const paymentMethods = [
  {
    id: "mpesa_primary",
    type: "M-Pesa",
    number: "+254 7XX XXX 456",
    isPrimary: true,
    isConnected: true,
    icon: Smartphone,
  },
  {
    id: "mpesa_secondary",
    type: "M-Pesa",
    number: "+254 7XX XXX 789",
    isPrimary: false,
    isConnected: true,
    icon: Smartphone,
  },
]

export function PaymentMethods() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Payment Methods</CardTitle>
        <Button variant="outline" size="sm" className="flex items-center gap-2 bg-transparent">
          <Plus className="h-4 w-4" />
          Add Method
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        {paymentMethods.map((method) => (
          <div key={method.id} className="flex items-center justify-between p-3 rounded-lg border border-border">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-green-100 dark:bg-green-900">
                <method.icon className="h-4 w-4 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{method.type}</span>
                  {method.isPrimary && (
                    <Badge variant="default" className="text-xs">
                      Primary
                    </Badge>
                  )}
                  <Badge variant={method.isConnected ? "default" : "secondary"} className="text-xs">
                    {method.isConnected ? "Connected" : "Disconnected"}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{method.number}</p>
              </div>
            </div>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
