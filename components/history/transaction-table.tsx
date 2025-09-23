"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ArrowUpRight, ArrowDownRight, ExternalLink, Eye } from "lucide-react"

const transactions = [
  {
    id: "tx_001",
    type: "sell",
    amount: "5.2 eKWh",
    price: "KES 52",
    total: "KES 270.40",
    counterparty: "House #47",
    status: "completed",
    timestamp: "2024-01-15 14:23",
    blockchainTx: "0x1a2b3c...",
    mpesaRef: "QGH7X8Y9Z1",
  },
  {
    id: "tx_002",
    type: "buy",
    amount: "3.1 eKWh",
    price: "KES 48",
    total: "KES 148.80",
    counterparty: "House #23",
    status: "completed",
    timestamp: "2024-01-15 13:45",
    blockchainTx: "0x2b3c4d...",
    mpesaRef: "QGH7X8Y9Z2",
  },
  {
    id: "tx_003",
    type: "sell",
    amount: "8.7 eKWh",
    price: "KES 51",
    total: "KES 443.70",
    counterparty: "House #12",
    status: "pending",
    timestamp: "2024-01-15 12:30",
    blockchainTx: "0x3c4d5e...",
    mpesaRef: "Pending",
  },
  {
    id: "tx_004",
    type: "buy",
    amount: "2.8 eKWh",
    price: "KES 49",
    total: "KES 137.20",
    counterparty: "House #89",
    status: "failed",
    timestamp: "2024-01-15 11:15",
    blockchainTx: "Failed",
    mpesaRef: "Failed",
  },
  {
    id: "tx_005",
    type: "sell",
    amount: "6.4 eKWh",
    price: "KES 53",
    total: "KES 339.20",
    counterparty: "House #34",
    status: "completed",
    timestamp: "2024-01-15 10:20",
    blockchainTx: "0x4d5e6f...",
    mpesaRef: "QGH7X8Y9Z5",
  },
]

export function TransactionTable() {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800 border-green-200">Completed</Badge>
      case "pending":
        return <Badge variant="secondary">Pending</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Transaction History</CardTitle>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="bg-transparent">
            Export CSV
          </Button>
          <Button variant="outline" size="sm" className="bg-transparent">
            <ExternalLink className="h-4 w-4 mr-2" />
            View on Blockchain
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Counterparty</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {tx.type === "sell" ? (
                        <ArrowUpRight className="h-4 w-4 text-red-500" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-green-500" />
                      )}
                      <span className="capitalize font-medium">{tx.type}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-medium">{tx.amount}</TableCell>
                  <TableCell>{tx.price}</TableCell>
                  <TableCell className="font-medium">{tx.total}</TableCell>
                  <TableCell>{tx.counterparty}</TableCell>
                  <TableCell>{getStatusBadge(tx.status)}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{tx.timestamp}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
