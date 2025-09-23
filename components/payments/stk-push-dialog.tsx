"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Smartphone, Loader2, CheckCircle, AlertCircle } from "lucide-react"

interface StkPushDialogProps {
  trigger: React.ReactNode
  amount: number
  description: string
}

export function StkPushDialog({ trigger, amount, description }: StkPushDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState("+254 7XX XXX 456")
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "success" | "failed">("idle")

  const handleStkPush = async () => {
    setStatus("sending")

    // Simulate STK push process
    setTimeout(() => {
      setStatus("sent")
      setTimeout(() => {
        setStatus("success") // or "failed" for error simulation
      }, 3000)
    }, 1000)
  }

  const getStatusContent = () => {
    switch (status) {
      case "sending":
        return (
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
            <p className="text-sm text-muted-foreground">Initiating payment request...</p>
          </div>
        )
      case "sent":
        return (
          <div className="text-center space-y-4">
            <Smartphone className="h-8 w-8 mx-auto text-blue-500" />
            <div>
              <p className="font-medium">Check your phone</p>
              <p className="text-sm text-muted-foreground">Enter your M-Pesa PIN to complete the payment</p>
            </div>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              Waiting for confirmation
            </Badge>
          </div>
        )
      case "success":
        return (
          <div className="text-center space-y-4">
            <CheckCircle className="h-8 w-8 mx-auto text-green-500" />
            <div>
              <p className="font-medium text-green-700">Payment Successful!</p>
              <p className="text-sm text-muted-foreground">Your energy tokens will be transferred shortly</p>
            </div>
            <Badge className="bg-green-100 text-green-800 border-green-200">Transaction Complete</Badge>
          </div>
        )
      case "failed":
        return (
          <div className="text-center space-y-4">
            <AlertCircle className="h-8 w-8 mx-auto text-red-500" />
            <div>
              <p className="font-medium text-red-700">Payment Failed</p>
              <p className="text-sm text-muted-foreground">Please check your M-Pesa balance and try again</p>
            </div>
            <Button variant="outline" onClick={() => setStatus("idle")}>
              Try Again
            </Button>
          </div>
        )
      default:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="phone">M-Pesa Phone Number</Label>
              <Input
                id="phone"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+254 7XX XXX XXX"
              />
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Amount:</span>
                <span className="font-medium">KES {amount}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Transaction Fee:</span>
                <span className="font-medium">KES 5.00</span>
              </div>
              <div className="flex justify-between text-sm font-medium border-t pt-2">
                <span>Total:</span>
                <span>KES {amount + 5}</span>
              </div>
            </div>

            <Button onClick={handleStkPush} className="w-full" size="lg">
              <Smartphone className="h-4 w-4 mr-2" />
              Send Payment Request
            </Button>
          </div>
        )
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5 text-green-600" />
            M-Pesa Payment
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="p-3 rounded-lg bg-muted">
            <p className="text-sm font-medium">{description}</p>
          </div>
          {getStatusContent()}
        </div>
      </DialogContent>
    </Dialog>
  )
}
