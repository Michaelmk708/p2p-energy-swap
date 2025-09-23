import { TransactionFilters } from "@/components/history/transaction-filters"
import { TransactionTable } from "@/components/history/transaction-table"
import { TransactionStats } from "@/components/history/transaction-stats"

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">Transaction History</h1>
        <p className="text-muted-foreground text-pretty">
          View and analyze your complete energy trading and payment history.
        </p>
      </div>

      {/* Stats Overview */}
      <TransactionStats />

      {/* Filters */}
      <TransactionFilters />

      {/* Transaction Table */}
      <TransactionTable />
    </div>
  )
}
