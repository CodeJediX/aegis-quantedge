package com.quantumx.aegis;

import java.io.*;
import java.util.*;

/** Offline native numerical engine. Fractions internally; one USD10m reference. */
public final class ResearchEngine {
    public static final String[] TICKERS={"SPY","EFA","EEM","AGG","GLD","XLE","XLK"};
    public static final double CAPITAL=10_000_000.0, COST=.001;
    public static final double[] SHOCK={-.25,-.30,-.35,-.12,-.10,-.25,-.35};
    public static final String TRAIN_END="2018-12-31", TEST_START="2023-01-01";
    public static final int WINDOW=756;
    public static final class Data {
        public String[] dates; public double[][] returns; public double[] rf;
        public LinkedHashMap<String,double[]> presets=new LinkedHashMap<>();
        public static Data read(Reader prices,Reader rates,Reader allocations)throws IOException {
            Data d=new Data(); ArrayList<String> dates=new ArrayList<>();ArrayList<double[]> rr=new ArrayList<>();
            BufferedReader p=new BufferedReader(prices);String header=p.readLine();
            if(header==null||!header.endsWith("SPY,EFA,EEM,AGG,GLD,XLE,XLK"))throw new IOException("Unexpected ETF universe");
            String line,previousDate="";double[] previous=null;
            while((line=p.readLine())!=null){String[] cells=line.split(",");if(cells.length!=8)throw new IOException("Incomplete prices");
                if(cells[0].compareTo(previousDate)<=0)throw new IOException("Dates must be strictly increasing");
                double[] now=new double[7];for(int j=0;j<7;j++){now[j]=Double.parseDouble(cells[j+1]);if(!Double.isFinite(now[j])||now[j]<=0)throw new IOException("Invalid price");}
                if(previous!=null){double[] r=new double[7];for(int j=0;j<7;j++)r[j]=now[j]/previous[j]-1;rr.add(r);dates.add(cells[0]);}
                previous=now;previousDate=cells[0];}
            d.dates=dates.toArray(new String[0]);d.returns=rr.toArray(new double[0][]);d.rf=new double[d.dates.length];
            HashMap<String,Double> rf=new HashMap<>();BufferedReader f=new BufferedReader(rates);f.readLine();while((line=f.readLine())!=null){String[] c=line.split(",");rf.put(c[0],Double.parseDouble(c[1]));}
            for(int i=0;i<d.rf.length;i++){Double value=rf.get(d.dates[i]);if(value==null||!Double.isFinite(value))throw new IOException("Missing lagged risk-free rate");d.rf[i]=value;}
            BufferedReader a=new BufferedReader(allocations);String[] names=a.readLine().split(",");for(int j=1;j<names.length;j++)d.presets.put(names[j],new double[7]);
            int row=0;while((line=a.readLine())!=null){String[] c=line.split(",");if(row>=7||!c[0].equals(TICKERS[row]))throw new IOException("Allocation order mismatch");for(int j=1;j<c.length;j++)d.presets.get(names[j])[row]=Double.parseDouble(c[j]);row++;}
            if(row!=7||d.dates.length<1000)throw new IOException("Incomplete research snapshot");return d;
        }
    }
    public static void validate(double[] w){double sum=0;if(w.length!=7)throw new IllegalArgumentException("Seven weights required");for(double x:w){if(!Double.isFinite(x)||x<0||x>1)throw new IllegalArgumentException("Weights must be finite and between 0% and 100%");sum+=x;}if(Math.abs(sum-1)>1e-7)throw new IllegalArgumentException("Weights must total 100%");}
    public static double dot(double[] a,double[] b){double s=0;for(int j=0;j<a.length;j++)s+=a[j]*b[j];return s;}
    public static double mean(double[] a){double s=0;for(double x:a)s+=x;return s/a.length;}
    public static double variance(double[] a){double m=mean(a),s=0;for(double x:a)s+=(x-m)*(x-m);return s/(a.length-1);}
    public static double quantile(double[] a,double q){double[] x=a.clone();Arrays.sort(x);double at=(x.length-1)*q;int lo=(int)Math.floor(at);int hi=(int)Math.ceil(at);return x[lo]+(at-lo)*(x[hi]-x[lo]);}
    public static double[] historical(double[] loss,double alpha){double q=quantile(loss,alpha),excess=0;for(double x:loss)excess+=Math.max(x-q,0);return new double[]{q,q+excess/loss.length/(1-alpha)};}
    public static double normalCdf(double x){if(x>8)return 1;if(x< -8)return 0;double z=x/Math.sqrt(2),term=z,sum=z;for(int n=1;n<150;n++){term*= -z*z/n;double next=term/(2*n+1);sum+=next;if(Math.abs(next)<1e-18)break;}return Math.max(0,Math.min(1,.5+sum/Math.sqrt(Math.PI)));}
    public static double inverseNormal(double p){double lo=-8,hi=8;for(int i=0;i<75;i++){double mid=(lo+hi)/2;if(normalCdf(mid)<p)lo=mid;else hi=mid;}return (lo+hi)/2;}
    public static double[] gaussian(double[] simple,double alpha){double[] log=new double[simple.length];for(int i=0;i<log.length;i++)log[i]=Math.log1p(simple[i]);double mu=mean(log),sd=Math.sqrt(variance(log));if(sd<1e-15)return new double[]{-Math.expm1(mu),-Math.expm1(mu)};double z=inverseNormal(1-alpha);return new double[]{1-Math.exp(mu+sd*z),1-Math.exp(mu+.5*sd*sd)*normalCdf(z-sd)/(1-alpha)};}
    public static double[] gross(Data d,double[] w){double[] g=new double[d.dates.length];for(int i=0;i<g.length;i++)g[i]=dot(d.returns[i],w);return g;}
    public static double[][] netPath(Data d,double[] w){double[] g=gross(d,w),net=g.clone(),turnover=new double[g.length];for(int i=1;i<g.length;i++){double traded=0;for(int j=0;j<7;j++)traded+=Math.abs(w[j]*(1+d.returns[i-1][j])/(1+g[i-1])-w[j]);turnover[i]=traded;net[i]=(1-COST*traded)*(1+g[i])-1;}return new double[][]{net,turnover};}
    public static int firstAt(Data d,String day){int i=0;while(i<d.dates.length&&d.dates[i].compareTo(day)<0)i++;return i;}
    public static double drawdown(double[] r){double wealth=1,peak=1,dd=0;for(double x:r){wealth*=1+x;peak=Math.max(peak,wealth);dd=Math.max(dd,1-wealth/peak);}return dd;}
    public static final class Scenario {public String name,start,end;public double terminal,drawdown;public double[] contributions,curve;}
    public static Scenario scenario(Data d,double[] w,int choice){Scenario s=new Scenario();s.contributions=new double[7];
        String[] names={"2008 GFC","2020 COVID","2022 rates","Funding squeeze"};s.name=names[choice];
        if(choice==3){s.terminal=dot(w,SHOCK);s.drawdown=Math.max(0,-s.terminal);for(int j=0;j<7;j++)s.contributions[j]=w[j]*SHOCK[j];s.curve=new double[]{1,1+s.terminal};s.start=s.end="Assumed simultaneous event";return s;}
        String[] starts={"2008-01-01","2020-02-19","2022-01-01"},ends={"2009-03-31","2020-03-31","2022-12-31"};
        int from=firstAt(d,starts[choice]),to=firstAt(d,ends[choice]);if(to<d.dates.length&&d.dates[to].equals(ends[choice]))to++;
        s.start=d.dates[from];s.end=d.dates[to-1];s.curve=new double[to-from+1];s.curve[0]=1;double peak=1;
        for(int i=from;i<to;i++){double wealth=s.curve[i-from];for(int j=0;j<7;j++)s.contributions[j]+=wealth*w[j]*d.returns[i][j];s.curve[i-from+1]=wealth*(1+dot(d.returns[i],w));peak=Math.max(peak,s.curve[i-from+1]);s.drawdown=Math.max(s.drawdown,1-s.curve[i-from+1]/peak);}s.terminal=s.curve[s.curve.length-1]-1;return s;
    }
    public static final class Check {public String label;public double value,limit;public boolean passed,asset;Check(String l,double v,double lim,boolean pass,boolean a){label=l;value=v;limit=lim;passed=pass;asset=a;}}
    public static final class Analysis {
        public double[] weights,testNet,wealth;public String name;public double cagr,vol,dd,sharpe,sortino,beta,jensen,information,calmar,treynor,turnover;
        public double expected,trainingVol,trainingDD,es99,var99,worstReplay,worstScenario;public ArrayList<Check> checks=new ArrayList<>();public int failures;public boolean assetFailure;
        public String recommendation(Backtest b){return assetFailure?"REJECT":failures>0||b==null||!b.passes()?"REVISE":"APPROVE";}
    }
    public static Analysis analyze(Data d,double[] w,String name){validate(w);Analysis a=new Analysis();a.weights=w.clone();a.name=name;double[][] pp=netPath(d,w);int test=firstAt(d,TEST_START),train=firstAt(d,"2019-01-01");
        a.testNet=Arrays.copyOfRange(pp[0],test,pp[0].length);double[] benchmark=Arrays.copyOfRange(netPath(d,new double[]{.6,0,0,.4,0,0,0})[0],test,pp[0].length);
        int n=a.testNet.length;a.wealth=new double[n];double wealth=1;for(int i=0;i<n;i++){wealth*=1+a.testNet[i];a.wealth[i]=wealth*CAPITAL;}a.cagr=Math.pow(wealth,252.0/n)-1;a.vol=Math.sqrt(variance(a.testNet)*252);a.dd=drawdown(a.testNet);
        double[] excess=new double[n],market=new double[n],active=new double[n];double downside=0;for(int i=0;i<n;i++){excess[i]=a.testNet[i]-d.rf[test+i];market[i]=d.returns[test+i][0]-d.rf[test+i];active[i]=a.testNet[i]-benchmark[i];downside+=Math.pow(Math.min(excess[i],0),2);a.turnover+=pp[1][test+i]*252.0/n;}
        a.sharpe=a.vol>0?mean(excess)*252/a.vol:Double.NaN;a.sortino=downside>0?mean(excess)*252/Math.sqrt(downside/n*252):Double.NaN;
        double cov=0,mx=mean(market),ex=mean(excess);for(int i=0;i<n;i++)cov+=(excess[i]-ex)*(market[i]-mx);a.beta=cov/(n-1)/variance(market);a.jensen=(ex-a.beta*mx)*252;a.treynor=ex*252/a.beta;a.information=mean(active)*252/Math.sqrt(variance(active)*252);a.calmar=a.dd>0?a.cagr/a.dd:Double.NaN;
        double[] means=new double[7];for(int i=0;i<train;i++)for(int j=0;j<7;j++)means[j]+=d.returns[i][j]/train;double universe=mean(means);for(int j=0;j<7;j++)a.expected+=w[j]*(.5*means[j]+.5*universe)*252;
        double v=0;for(int j=0;j<7;j++)for(int k=0;k<7;k++){double c=0;for(int i=0;i<train;i++)c+=(d.returns[i][j]-means[j])*(d.returns[i][k]-means[k]);c=c/(train-1)*252;v+=w[j]*w[k]*c*(j==k?1:.9);}a.trainingVol=Math.sqrt(v);a.trainingDD=drawdown(Arrays.copyOf(pp[0],train));
        double[] gross=gross(d,w),loss=new double[WINDOW];for(int i=0;i<WINDOW;i++)loss[i]=-gross[gross.length-WINDOW+i];double[] hs=historical(loss,.99);a.var99=hs[0];a.es99=hs[1];for(int i=0;i<4;i++){Scenario s=scenario(d,w,i);if(i<3)a.worstReplay=Math.max(a.worstReplay,s.drawdown);a.worstScenario=Math.max(a.worstScenario,-s.terminal);}
        double[] low={0,0,0,.35,.05,0,0},high={.25,.20,.15,.70,.20,.10,.20};for(int j=0;j<7;j++)add(a,TICKERS[j]+" weight",w[j],high[j],w[j]>=low[j]-1e-8&&w[j]<=high[j]+1e-8,true);
        double eq=w[0]+w[1]+w[2]+w[5]+w[6];add(a,"Combined equity",eq,.50,eq>=.20-1e-8&&eq<=.50+1e-8,true);
        add(a,"Held-out annual volatility",a.vol,.10,a.vol<=.10+1e-8,false);add(a,"Held-out maximum drawdown",a.dd,.15,a.dd<=.15+1e-8,false);add(a,"Training maximum net drawdown",a.trainingDD,.15,a.trainingDD<=.15+1e-8,false);add(a,"Current daily historical ES99",a.es99,.025,a.es99<=.025+1e-8,false);add(a,"Worst scenario terminal loss",a.worstScenario,.15,a.worstScenario<=.15+1e-8,false);add(a,"Worst historical replay drawdown",a.worstReplay,.15,a.worstReplay<=.15+1e-8,false);add(a,"Training estimated return",a.expected,.04,a.expected>=.04-1e-8,false);return a;
    }
    private static void add(Analysis a,String l,double v,double limit,boolean ok,boolean asset){a.checks.add(new Check(l,v,limit,ok,asset));if(!ok){a.failures++;a.assetFailure|=asset;}}
    public static final class Backtest {public int n,hits,lastN,lastHits;public double kupiec,independence,joint;public String traffic;public double[] losses,forecasts;public boolean passes(){return kupiec>=.05&&independence>=.05&&joint>=.05&&"Green".equals(traffic);}}
    private static double logTerm(int count,double p){return count==0?0:p<=0?Double.NEGATIVE_INFINITY:count*Math.log(p);}
    private static double logBin(int k,int n,double p){return logTerm(k,p)+logTerm(n-k,1-p);}
    public static Backtest backtest(Data d,double[] w){validate(w);double[] g=gross(d,w);int start=firstAt(d,TEST_START);Backtest b=new Backtest();b.n=g.length-start;b.lastN=Math.min(250,b.n);b.losses=new double[b.n];b.forecasts=new double[b.n];boolean[] hit=new boolean[b.n];int[][] transitions=new int[2][2];
        for(int i=start;i<g.length;i++){double[] loss=new double[WINDOW];for(int j=0;j<WINDOW;j++)loss[j]=-g[i-WINDOW+j];int k=i-start;b.losses[k]=-g[i];b.forecasts[k]=quantile(loss,.99);hit[k]=b.losses[k]>b.forecasts[k];if(hit[k]){b.hits++;if(k>=b.n-b.lastN)b.lastHits++;}if(k>0)transitions[hit[k-1]?1:0][hit[k]?1:0]++;}
        double lr=Math.max(0,2*(logBin(b.hits,b.n,(double)b.hits/b.n)-logBin(b.hits,b.n,.01)));b.kupiec=2*(1-normalCdf(Math.sqrt(lr)));int n0=transitions[0][0]+transitions[0][1],n1=transitions[1][0]+transitions[1][1];
        if(n0==0||n1==0){b.independence=b.joint=Double.NaN;}else{double pi=(double)(transitions[0][1]+transitions[1][1])/(b.n-1);double alt=logBin(transitions[0][1],n0,(double)transitions[0][1]/n0)+logBin(transitions[1][1],n1,(double)transitions[1][1]/n1);double nul=logBin(transitions[0][1]+transitions[1][1],b.n-1,pi);double ind=Math.max(0,2*(alt-nul));b.independence=2*(1-normalCdf(Math.sqrt(ind)));b.joint=Math.exp(-(lr+ind)/2);}
        b.traffic=b.lastN==250?(b.lastHits<=4?"Green":b.lastHits<=9?"Amber":"Red"):"N/A";return b;
    }
    public static double[] whatIf(double[] w,double equity,double gold,double bps,double duration){validate(w);double[] s=new double[7];for(int j=0;j<7;j++)s[j]=w[j]*(j==3?-duration*bps/10000:j==4?gold:equity);return s;}
}
