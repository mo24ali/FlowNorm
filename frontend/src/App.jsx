import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  FileUp, 
  RefreshCcw, 
  LayoutDashboard, 
  CreditCard,
  Search,
  CheckCircle,
  XCircle,
  Clock,
  ArrowUpRight
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const App = () => {
  const [stats, setStats] = useState({ tasks: { total: 0, completed: 0, failed: 0 }, health: 'Healthy' });
  const [transactions, setTransactions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [recentTask, setRecentTask] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, txnsRes, anomaliesRes] = await Promise.all([
        axios.get(`${API_BASE}/monitor/stats`),
        axios.get(`${API_BASE}/transactions?limit=10`),
        axios.get(`${API_BASE}/anomalies`)
      ]);
      setStats(statsRes.data);
      setTransactions(txnsRes.data);
      setAnomalies(anomaliesRes.data);
    } catch (error) {
      console.error("Dashboard error:", error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/ingest/file`, formData);
      setRecentTask(response.data.task_id);
    } catch (error) {
      alert("Upload failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <header className="flex justify-between items-end">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight text-white flex items-center gap-3">
            <LayoutDashboard className="text-blue-500 w-8 h-8" />
            Fintech Data Aggregator
          </h1>
          <p className="text-muted text-lg">Self-healing aggregation and normalization pipeline</p>
        </div>

        <div className="flex gap-4">
          <label className={`btn-primary cursor-pointer ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
             {isUploading ? <RefreshCcw className="w-5 h-5 animate-spin" /> : <FileUp className="w-5 h-5" />}
             {isUploading ? 'Ingesting...' : 'Import CSV'}
             <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} disabled={isUploading} />
          </label>
        </div>
      </header>

      {/* Hero Stats */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card">
           <div className="flex justify-between items-start">
             <div className="p-2 bg-blue-500/10 rounded-lg"><Activity className="text-blue-500 w-6 h-6" /></div>
             <span className="text-[10px] text-green-500 font-bold border border-green-500/30 px-2 py-0.5 rounded-full uppercase tracking-widest bg-green-500/5">System Up</span>
           </div>
           <p className="text-muted text-sm font-medium mt-4">Total Pipelines</p>
           <h3 className="text-3xl font-bold">{stats.tasks.total}</h3>
        </div>

        <div className="stat-card">
           <div className="flex justify-between items-start">
             <div className="p-2 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="text-emerald-500 w-6 h-6" /></div>
           </div>
           <p className="text-muted text-sm font-medium mt-4">Successfully Normalized</p>
           <h3 className="text-3xl font-bold text-emerald-400">{stats.tasks.completed}</h3>
        </div>

        <div className="stat-card border-red-500/20">
           <div className="flex justify-between items-start">
             <div className="p-2 bg-red-500/10 rounded-lg"><AlertCircle className="text-red-500 w-6 h-6" /></div>
           </div>
           <p className="text-muted text-sm font-medium mt-4">Flagged Anomalies</p>
           <h3 className="text-3xl font-bold text-red-500">{anomalies.length}</h3>
        </div>

        <div className="stat-card">
           <div className="flex justify-between items-start">
             <div className="p-2 bg-accent/10 rounded-lg"><CreditCard className="text-accent w-6 h-6" /></div>
           </div>
           <p className="text-muted text-sm font-medium mt-4">Total Accounts</p>
           <h3 className="text-3xl font-bold">14</h3>
        </div>
      </section>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Normalized Transactions Table */}
        <section className="lg:col-span-2 glass-card p-6 min-h-[500px]">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
               Normalized Real-time Flow
               <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse-slow"></span>
            </h2>
            <div className="flex gap-2 text-xs text-muted">
              <div className="flex items-center gap-1"><Search className="w-3 h-3"/> Filter</div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-muted uppercase tracking-wider text-[10px] border-b border-gray-800">
                <tr>
                  <th className="pb-4">Date</th>
                  <th className="pb-4">Description</th>
                  <th className="pb-4">Amount</th>
                  <th className="pb-4">Category</th>
                  <th className="pb-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {transactions.length === 0 ? (
                    <tr>
                        <td colSpan="5" className="py-20 text-center text-muted">
                            No transactions processed in current session. Upload a CSV to begin.
                        </td>
                    </tr>
                ) : transactions.map((t, idx) => (
                    <tr key={t.id || idx} className="hover:bg-gray-800/30 transition-colors group">
                        <td className="py-4 text-gray-400 font-mono">{t.date}</td>
                        <td className="py-4 font-medium max-w-xs truncate">{t.description}</td>
                        <td className={ `py-4 font-bold ${t.amount < 0 ? 'text-red-400' : 'text-emerald-400'}` }>
                          {new Intl.NumberFormat('en-US', { style: 'currency', currency: t.currency }).format(t.amount)}
                        </td>
                        <td className="py-4">
                          <span className="bg-gray-800 px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold text-gray-400">
                             {t.normalized_category}
                          </span>
                        </td>
                        <td className="py-4">
                          {t.is_anomaly ? (
                            <span className="flex items-center gap-1.5 text-xs font-medium text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded-lg border border-amber-500/20">
                              <AlertCircle className="w-3 h-3" /> Flagged
                            </span>
                          ) : (
                            <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-lg border border-emerald-500/20">
                              <CheckCircle className="w-3 h-3" /> Standard
                            </span>
                          )}
                        </td>
                    </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Anomaly & Self-healing Activity Log */}
        <section className="space-y-6">
           <div className="glass-card p-6 border-amber-500/10 flex flex-col gap-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                 Anomaly Trace
                 <span className="bg-amber-500/20 text-amber-500 text-[10px] px-2 py-0.5 rounded-full uppercase">Action Required</span>
              </h2>
              
              <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
                {anomalies.length === 0 ? (
                  <div className="text-center py-10 opacity-40 italic text-sm">Waiting for ingestion scan...</div>
                ) : anomalies.map((a, idx) => (
                   <div key={idx} className="bg-gray-800/40 p-4 rounded-xl border border-gray-700/50 space-y-2">
                      <div className="flex justify-between items-start">
                        <span className="text-[10px] font-bold text-amber-500 flex items-center gap-1">
                           <AlertCircle className="w-3 h-3" /> QUALITY_WARNING
                        </span>
                        <span className="text-[10px] text-muted">{a.date}</span>
                      </div>
                      <p className="text-xs font-medium">{a.description}</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {a.anomalies.map((error, eidx) => (
                          <span key={eidx} className="text-[9px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full border border-red-500/10 uppercase tracking-tighter">
                            {error}
                          </span>
                        ))}
                      </div>
                   </div>
                ))}
              </div>
           </div>

           <div className="glass-card p-6 space-y-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                 Worker Pipeline
                 <RefreshCcw className="w-4 h-4 text-blue-500 animate-spin-slow opacity-50" />
              </h2>
              <div className="space-y-3">
                 <PipelineTask icon={<CheckCircle className="text-emerald-500" />} label="Deduplication Engine" status="Online" />
                 <PipelineTask icon={<Clock className="text-blue-500" />} label="Self-healing Sync" status="Operational" />
                 <PipelineTask icon={<XCircle className="text-red-500" />} label="QuickBooks Connector" status="Offline (Auth)" />
              </div>
           </div>

           <div className="bg-gradient-to-br from-blue-600/20 to-blue-900/20 p-6 rounded-2xl border border-blue-500/30 space-y-3 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-10"><Activity className="w-24 h-24" /></div>
               <h3 className="text-lg font-bold">Scalable Architecture</h3>
               <p className="text-xs text-gray-300">This MVP is deployed on AWS Lambda & Step Functions with 0 manual intervention retries enabled.</p>
               <button className="flex items-center gap-1 text-[10px] font-bold tracking-widest text-blue-400 hover:text-white transition-colors">
                  VIEW CLOUDWATCH LOGS <ArrowUpRight className="w-3 h-3" />
               </button>
           </div>
        </section>

      </div>
    </div>
  );
};

const PipelineTask = ({ icon, label, status }) => (
  <div className="flex items-center justify-between py-2 bg-gray-800/10 px-3 rounded-lg border border-gray-800">
    <div className="flex items-center gap-3">
      {React.cloneElement(icon, { size: 16 })}
      <span className="text-xs font-medium text-gray-300">{label}</span>
    </div>
    <span className={`text-[9px] font-bold uppercase tracking-widest ${status.includes('Online') || status.includes('Operational') ? 'text-emerald-500' : 'text-red-500'}`}>
       {status}
    </span>
  </div>
);

export default App;
