import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowUpRight, ArrowDownRight, Receipt } from "lucide-react";

// Dummy transaction data
const transactions = [
  { id: "TX001", type: "buy", seller: "SolarFarm_42", tokens: 50, price: 12, total: 600, date: "2025-10-01", status: "completed" },
  { id: "TX002", type: "sell", buyer: "EcoHome_91", tokens: 30, price: 13, total: 390, date: "2025-09-30", status: "completed" },
  { id: "TX003", type: "buy", seller: "GreenVilla_23", tokens: 25, price: 11.5, total: 287.5, date: "2025-09-29", status: "completed" },
  { id: "TX004", type: "sell", buyer: "SunnyRoof_15", tokens: 45, price: 12.5, total: 562.5, date: "2025-09-28", status: "completed" },
  { id: "TX005", type: "buy", seller: "WindPower_67", tokens: 40, price: 11, total: 440, date: "2025-09-27", status: "completed" },
];

export default function Transactions() {
  const totalBought = transactions
    .filter(t => t.type === "buy")
    .reduce((sum, t) => sum + t.tokens, 0);

  const totalSold = transactions
    .filter(t => t.type === "sell")
    .reduce((sum, t) => sum + t.tokens, 0);

  const totalSpent = transactions
    .filter(t => t.type === "buy")
    .reduce((sum, t) => sum + t.total, 0);

  const totalEarned = transactions
    .filter(t => t.type === "sell")
    .reduce((sum, t) => sum + t.total, 0);

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Transactions</h1>
          <p className="text-muted-foreground">Your complete trading history</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowDownRight className="h-4 w-4 text-primary" />
                Tokens Bought
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{totalBought}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowUpRight className="h-4 w-4 text-accent" />
                Tokens Sold
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{totalSold}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Spent</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">
                KES {totalSpent.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Earned</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                KES {totalEarned.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Transaction History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5 text-primary" />
              Transaction History
            </CardTitle>
            <CardDescription>All your buy and sell orders</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Partner</TableHead>
                    <TableHead className="text-right">Tokens</TableHead>
                    <TableHead className="text-right">Price/Token</TableHead>
                    <TableHead className="text-right">Total (KES)</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell className="font-mono text-sm">{tx.id}</TableCell>
                      <TableCell>
                        {tx.type === "buy" ? (
                          <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                            <ArrowDownRight className="h-3 w-3" />
                            Buy
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="flex items-center gap-1 w-fit">
                            <ArrowUpRight className="h-3 w-3" />
                            Sell
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="font-medium">
                        {tx.type === "buy" ? tx.seller : tx.buyer}
                      </TableCell>
                      <TableCell className="text-right font-medium">{tx.tokens}</TableCell>
                      <TableCell className="text-right">KES {tx.price}</TableCell>
                      <TableCell className="text-right font-bold">
                        KES {tx.total.toFixed(2)}
                      </TableCell>
                      <TableCell>{tx.date}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="bg-primary/10 text-primary">
                          {tx.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
