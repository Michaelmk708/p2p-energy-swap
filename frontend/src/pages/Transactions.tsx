import React, { useEffect, useState } from 'react';
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowUpRight, ArrowDownRight, Receipt, Zap } from "lucide-react";
import api from "@/lib/api";

export default function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [summary, setSummary] = useState({
    total_minted: 0,
    total_bought: 0,
    total_sold: 0,
    total_spent: 0,
    total_earned: 0,
    transaction_count: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await api.get('/transactions/');
        setTransactions(response.data.transactions || []);
        setSummary(response.data.summary || summary);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
        // Keep empty state on error
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const totalBought = summary.total_bought;
  const totalSold = summary.total_sold;
  const totalSpent = summary.total_spent;
  const totalEarned = summary.total_earned;

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
                <Zap className="h-4 w-4 text-primary" />
                Tokens Minted
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{summary.total_minted}</div>
              <div className="text-xs text-muted-foreground">From energy exports</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <ArrowDownRight className="h-4 w-4 text-blue-600" />
                Tokens Bought
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{totalBought}</div>
              <div className="text-xs text-muted-foreground">From marketplace</div>
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
              <div className="text-xs text-muted-foreground">On marketplace</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Net Earned</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                KES {(totalEarned - totalSpent).toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">Earned - Spent</div>
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
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-muted-foreground">Loading transactions...</div>
              </div>
            ) : transactions.length === 0 ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <Receipt className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <div className="text-lg font-medium text-foreground">No transactions yet</div>
                  <div className="text-sm text-muted-foreground">Your trading activity will appear here</div>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Transaction ID</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Description</TableHead>
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
                          {tx.type === "mint" ? (
                            <Badge variant="default" className="flex items-center gap-1 w-fit bg-primary">
                              <Zap className="h-3 w-3" />
                              Mint
                            </Badge>
                          ) : tx.type === "buy" ? (
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
                        <TableCell className="font-medium max-w-xs">
                          <div className="truncate" title={tx.description}>
                            {tx.description || `${tx.type} transaction`}
                          </div>
                          {tx.seller && <div className="text-xs text-muted-foreground">with {tx.seller}</div>}
                        </TableCell>
                        <TableCell className="text-right font-medium">{tx.amount}</TableCell>
                        <TableCell className="text-right">
                          {tx.price_per_token ? `KES ${tx.price_per_token.toFixed(2)}` : '—'}
                        </TableCell>
                        <TableCell className="text-right font-bold">
                          {tx.total_cost ? `KES ${tx.total_cost.toFixed(2)}` : '—'}
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {new Date(tx.timestamp * 1000).toLocaleDateString()}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(tx.timestamp * 1000).toLocaleTimeString()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            {tx.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
