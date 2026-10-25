import com.quantumx.aegis.ResearchEngine;
import java.io.*;
import java.util.*;

/** Independent JVM regression runner against Python-generated numerical references. */
public class EngineReferenceTest {
    public static void main(String[] args)throws Exception{
        File dir=new File(args[0]);ResearchEngine.Data d=ResearchEngine.Data.read(new FileReader(new File(dir,"adjusted_prices.csv")),new FileReader(new File(dir,"risk_free.csv")),new FileReader(new File(dir,"allocations.csv")));
        LinkedHashMap<String,double[]> allocations=new LinkedHashMap<>(d.presets);allocations.put("Custom 20-60-20",new double[]{.2,0,0,.6,.2,0,0});HashMap<String,Double> got=new HashMap<>();
        for(Map.Entry<String,double[]> entry:allocations.entrySet()){String n=entry.getKey();double[] w=entry.getValue();ResearchEngine.Analysis a=ResearchEngine.analyze(d,w,n);
            String[] keys={"CAGR","volatility","max_drawdown","Sharpe","Sortino","beta","Jensen_alpha","information_ratio","Calmar","Treynor","annual_turnover","expected_return","training_volatility","training_drawdown","ES99","failed_checks"};
            double[] values={a.cagr,a.vol,a.dd,a.sharpe,a.sortino,a.beta,a.jensen,a.information,a.calmar,a.treynor,a.turnover,a.expected,a.trainingVol,a.trainingDD,a.es99,a.failures};for(int i=0;i<keys.length;i++)got.put(n+"::"+keys[i],values[i]);
            double[] g=ResearchEngine.gross(d,w),recent=Arrays.copyOfRange(g,g.length-756,g.length),loss=recent.clone();for(int i=0;i<loss.length;i++)loss[i]= -loss[i];
            for(double alpha:new double[]{.90,.95,.99}){double[] hs=ResearchEngine.historical(loss,alpha),gauss=ResearchEngine.gaussian(recent,alpha);String confidence=String.format(Locale.US,"%.2f",alpha);got.put(n+"::HS_VaR_"+confidence,hs[0]);got.put(n+"::HS_ES_"+confidence,hs[1]);got.put(n+"::Gaussian_VaR_"+confidence,gauss[0]);got.put(n+"::Gaussian_ES_"+confidence,gauss[1]);}
            for(int choice=0;choice<4;choice++){ResearchEngine.Scenario s=ResearchEngine.scenario(d,w,choice);got.put(n+"::stress_"+choice+"_return",s.terminal);got.put(n+"::stress_"+choice+"_drawdown",s.drawdown);double sum=0;for(double v:s.contributions)sum+=v;if(Math.abs(sum-s.terminal)>1e-10)throw new AssertionError("Stress contribution additivity");}
        }
        ResearchEngine.Backtest b=ResearchEngine.backtest(d,d.presets.get("AEGIS minimum variance"));got.put("Backtest::n",(double)b.n);got.put("Backtest::hits",(double)b.hits);got.put("Backtest::last_hits",(double)b.lastHits);got.put("Backtest::kupiec_p",b.kupiec);got.put("Backtest::independence_p",b.independence);got.put("Backtest::conditional_p",b.joint);
        BufferedReader expected=new BufferedReader(new FileReader(new File(dir,"python_reference.csv")));expected.readLine();String line;int checks=0;double worst=0;while((line=expected.readLine())!=null){String[] c=line.split(",");Double actual=got.get(c[0]);double value=Double.parseDouble(c[1]);if(Double.isNaN(value)){if(actual==null||!Double.isNaN(actual))throw new AssertionError("Unavailable diagnostic misreported: "+c[0]);checks++;continue;}if(actual==null||!Double.isFinite(actual)||Math.abs(actual-value)>2e-9)throw new AssertionError(c[0]+" Java="+actual+" Python="+value);worst=Math.max(worst,Math.abs(actual-value));checks++;}
        try{ResearchEngine.validate(new double[]{1,1,0,0,0,0,0});throw new AssertionError("Malformed weights accepted");}catch(IllegalArgumentException ok){}
        double[] shock=ResearchEngine.whatIf(new double[]{.2,0,0,.6,.2,0,0},-.2,-.05,100,6);double total=0;for(double v:shock)total+=v;if(Math.abs(total+.086)>1e-12)throw new AssertionError("What-if units");
        System.out.println("Native engine reference checks passed: "+checks+"; maximum absolute difference="+worst);
    }
}
