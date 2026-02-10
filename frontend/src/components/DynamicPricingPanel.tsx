import React from 'react';

export const DynamicPricingPanel: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-slate-700 dark:to-slate-800 rounded-lg shadow-lg p-6 border border-indigo-200 dark:border-slate-600">
      <h4 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Pricing Strategy Model</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        {/* Peak Solar */}
        <div className="space-y-2">
          <div className="bg-white dark:bg-slate-700 rounded p-3 shadow-sm border-l-4 border-green-500">
            <div className="flex justify-between items-center">
              <p className="font-semibold text-slate-800 dark:text-white">☀️ Peak Solar</p>
              <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">Best Value</span>
            </div>
            <p className="text-gray-600 dark:text-gray-300 text-xs mt-1">10:00 AM - 4:00 PM</p>
            <p className="text-green-600 font-bold text-lg">0.6x <span className="text-xs font-normal text-gray-500">Base Price</span></p>
            <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
              High solar production saturates the grid. Energy is cheapest.
            </p>
          </div>
        </div>

        {/* Early Morning */}
        <div className="space-y-2">
          <div className="bg-white dark:bg-slate-700 rounded p-3 shadow-sm border-l-4 border-yellow-500">
            <div className="flex justify-between items-center">
              <p className="font-semibold text-slate-800 dark:text-white">🌅 Early Morning</p>
              <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 px-2 py-1 rounded-full">Moderate</span>
            </div>
            <p className="text-gray-600 dark:text-gray-300 text-xs mt-1">7:00 AM - 10:00 AM</p>
            <p className="text-yellow-600 font-bold text-lg">0.85x <span className="text-xs font-normal text-gray-500">Base Price</span></p>
            <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
              Demand rises as people wake up; solar output is just starting.
            </p>
          </div>
        </div>

        {/* Evening Peak */}
        <div className="space-y-2">
          <div className="bg-white dark:bg-slate-700 rounded p-3 shadow-sm border-l-4 border-orange-500">
            <div className="flex justify-between items-center">
              <p className="font-semibold text-slate-800 dark:text-white">🌄 Evening Peak</p>
              <span className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300 px-2 py-1 rounded-full">Expensive</span>
            </div>
            <p className="text-gray-600 dark:text-gray-300 text-xs mt-1">4:00 PM - 7:00 PM</p>
            <p className="text-orange-600 font-bold text-lg">1.4x <span className="text-xs font-normal text-gray-500">Base Price</span></p>
            <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
              Solar generation drops while household consumption peaks.
            </p>
          </div>
        </div>

        {/* Night */}
        <div className="space-y-2">
          <div className="bg-white dark:bg-slate-700 rounded p-3 shadow-sm border-l-4 border-red-500">
            <div className="flex justify-between items-center">
              <p className="font-semibold text-slate-800 dark:text-white">🌙 Night</p>
              <span className="text-xs bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 px-2 py-1 rounded-full">Premium</span>
            </div>
            <p className="text-gray-600 dark:text-gray-300 text-xs mt-1">7:00 PM - 7:00 AM</p>
            <p className="text-red-600 font-bold text-lg">1.8x <span className="text-xs font-normal text-gray-500">Base Price</span></p>
            <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">
              Grid relies on stored energy or expensive imports.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};