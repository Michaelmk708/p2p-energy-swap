"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, ArrowDownRight, ExternalLink, Clock } from "lucide-react"

const paymentHistory = [
  {
    id: "pay_001",
    type: "received",
    amount: 260,
    description: "Energy sale to House #47",
    mpesaRef: "QGH7X8Y9Z1",
    timestamp: "2 min ago",
    status: "completed",
  },
  {
    id: "pay_002",
    type: "sent",
    amount: 155,
    description: "Energy purchase from House #23",
    mpesaRef: "QGH7X8Y9Z2",
    timestamp: "15 min ago",
    status: "completed",
  },
  {
    id: "pay_003",
    type: "received",
    amount: 435,
    description: "Energy sale to House #12",
    mpesaRef: "QGH7X8Y9Z3",
    timestamp: "1 hour ago",
    status: "pending",
  },
  {
    id: "pay_004",
    type: "sent",
    amount: 89,
    description: "Platform fee deduction",
    mpesaRef: "QGH7X8Y9Z4",
    timestamp: "2 hours ago",
    status: "completed",
  },
]

export function PaymentHistory() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Payment History</CardTitle>
        <Button variant="ghost" size="sm" className="flex items-center gap-1">
          View All
          <ExternalLink className="h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {paymentHistory.map((payment) => (
            <div key={payment.id} className="flex items-center justify-between p-3 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-full ${
                    payment.type === "received" ? "bg-green-100 dark:bg-green-900" : "bg-red-100 dark:bg-red-900"
                  }`}
                >
                  {payment.type === "received" ? (
                    <ArrowDownRight className="h-4 w-4 text-green-600 dark:text-green-400" />
                  ) : (
                    <ArrowUpRight className="h-4 w-4 text-red-600 dark:text-red-400" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{payment.description}</span>
                    <Badge variant={payment.status === "completed" ? "default" : "secondary"}>{payment.status}</Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {payment.timestamp}
                    </div>
                    <span>Ref: {payment.mpesaRef}</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div
                  className={`font-medium text-sm ${payment.type === "received" ? "text-green-600" : "text-red-600"}`}
                >
                  {payment.type === "received" ? "+" : "-"}KES {payment.amount}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
