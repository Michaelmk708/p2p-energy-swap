import { MpesaBalance } from "@/components/payments/mpesa-balance"
import { PaymentMethods } from "@/components/payments/payment-methods"
import { PaymentHistory } from "@/components/payments/payment-history"
import { StkPushDialog } from "@/components/payments/stk-push-dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, Plus } from "lucide-react"

export default function PaymentsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Payments & Wallet</h1>
        <p className="text-muted-foreground text-pretty">
          Manage your M-Pesa wallet, payment methods, and transaction history.
        </p>
      </div>

      {/* Balance and Quick Actions */}
      <div className="grid gap-6 md:grid-cols-3">
        <MpesaBalance />

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <StkPushDialog
              trigger={
                <Button className="w-full flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add Funds
                </Button>
              }
              amount={1000}
              description="Top up M-Pesa wallet for energy trading"
            />

            <Button variant="outline" className="w-full flex items-center gap-2 bg-transparent">
              <ArrowUpRight className="h-4 w-4" />
              Withdraw to Bank
            </Button>

            <StkPushDialog
              trigger={
                <Button variant="outline" className="w-full flex items-center gap-2 bg-transparent">
                  <ArrowDownRight className="h-4 w-4" />
                  Pay Energy Bill
                </Button>
              }
              amount={450}
              description="Pay monthly energy consumption bill"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Transaction Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">This Month:</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-green-600">Received</span>
                <span className="font-medium text-green-600">+KES 2,340</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-red-600">Spent</span>
                <span className="font-medium text-red-600">-KES 890</span>
              </div>
              <div className="flex justify-between font-medium border-t pt-2">
                <span>Net Income</span>
                <span className="text-green-600">+KES 1,450</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Payment Methods and History */}
      <div className="grid gap-6 lg:grid-cols-2">
        <PaymentMethods />
        <PaymentHistory />
      </div>
    </div>
  )
}
