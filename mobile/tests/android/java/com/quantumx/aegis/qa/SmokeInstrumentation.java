package com.quantumx.aegis.qa;
import android.app.*;
import android.content.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.graphics.Bitmap;
import android.view.accessibility.AccessibilityNodeInfo;
import android.net.Uri;
import java.io.*;
import java.util.*;
import com.quantumx.aegis.*;

/** Framework instrumentation against the actual signed APK on a real emulator. */
public final class SmokeInstrumentation extends Instrumentation {
    private MainActivity a;private final ArrayList<String> checks=new ArrayList<>();private File shots;
    @Override public void onCreate(Bundle args){super.onCreate(args);start();}
    private void main(Runnable r){runOnMainSync(r);waitForIdleSync();SystemClock.sleep(150);}
    private void ok(boolean condition,String name){if(!condition)throw new AssertionError(name);checks.add(name);}
    private void ready()throws Exception{for(int i=0;i<300;i++){if(a.analysis!=null&&a.findViewById(100)!=null){waitForIdleSync();SystemClock.sleep(250);return;}SystemClock.sleep(100);}throw new AssertionError("App failed to become ready");}
    private void shot(String name)throws Exception{waitForIdleSync();SystemClock.sleep(300);Bitmap b=getUiAutomation().takeScreenshot();if(b==null)throw new IOException("No emulator screenshot");try(OutputStream out=new FileOutputStream(new File(shots,name+".png"))){b.compress(Bitmap.CompressFormat.PNG,100,out);}b.recycle();}
    private void tab(int n){main(()->a.findViewById(100+n).performClick());}
    private ScrollView scroll(View v){if(v instanceof ScrollView)return (ScrollView)v;if(v instanceof ViewGroup){for(int i=0;i<((ViewGroup)v).getChildCount();i++){ScrollView found=scroll(((ViewGroup)v).getChildAt(i));if(found!=null)return found;}}return null;}
    private void down(){main(()->{ScrollView s=scroll(a.getWindow().getDecorView());s.fullScroll(View.FOCUS_DOWN);});}
    private boolean contains(View view,String text){if(view instanceof TextView&&((TextView)view).getText().toString().contains(text))return true;if(view instanceof ViewGroup)for(int i=0;i<((ViewGroup)view).getChildCount();i++)if(contains(((ViewGroup)view).getChildAt(i),text))return true;return false;}
    private View exact(View view,String text){if(view instanceof TextView&&((TextView)view).getText().toString().equals(text))return view;if(view instanceof ViewGroup)for(int i=0;i<((ViewGroup)view).getChildCount();i++){View found=exact(((ViewGroup)view).getChildAt(i),text);if(found!=null)return found;}return null;}
    private byte[] bytes(InputStream input)throws IOException{try(InputStream in=input;ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return out.toByteArray();}}
    @Override public void onStart(){Bundle result=new Bundle();try{
        Intent intent=new Intent();intent.setClassName("com.quantumx.aegis","com.quantumx.aegis.MainActivity");intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);a=(MainActivity)startActivitySync(intent);ready();shots=new File(getTargetContext().getExternalFilesDir(null),"qa-screenshots");shots.mkdirs();
        ok(a.analysis.failures==3,"Default policy has exactly three genuine failures");ok("REVISE".equals(a.analysis.recommendation(a.validation)),"Default recommendation remains REVISE");ok(a.validation.n==939&&a.validation.hits==8&&a.validation.lastHits==4,"Native real rolling validation matches reference windows");shot("01_native_decision_dashboard");down();shot("02_native_interactive_capital_chart");
        tab(1);ok(a.findViewById(226)!=null,"Seven native weight inputs rendered");shot("03_native_portfolio_editor");double[] before=a.analysis.weights.clone();
        main(()->{((EditText)a.findViewById(220)).setText("99");a.findViewById(230).performClick();});ok(Arrays.equals(before,a.analysis.weights),"Malformed weight sum cannot replace valid allocation");
        main(()->{String[] values={"20","0","0","60","20","0","0"};for(int i=0;i<7;i++)((EditText)a.findViewById(220+i)).setText(values[i]);a.findViewById(230).performClick();});ready();ok(Math.abs(a.analysis.weights[3]-.6)<1e-12,"Valid custom weights applied to the native calculation engine");ok(a.validation==null,"Custom validation is not borrowed from reference weights");
        tab(2);ok(a.findViewById(300)!=null,"Native risk confidence control is available");shot("04_native_selected_risk");main(()->((Spinner)a.findViewById(300)).setSelection(1));ok(contains(a.getWindow().getDecorView(),"95% confidence"),"95 percent confidence selection works");
        main(()->a.findViewById(301).performClick());ready();for(int i=0;i<200&&a.validation==null;i++)SystemClock.sleep(100);ok(a.validation!=null&&a.validation.n==939,"Custom Historical99 rolling validation actually executes");down();shot("05_native_custom_rolling_validation");
        tab(1);int version=1;while(exact(a.getWindow().getDecorView(),"Load · Research example "+version)!=null)version++;final String savedName="Research example "+version;
        main(()->{((EditText)a.findViewById(240)).setText(savedName);a.findViewById(241).performClick();});ok(exact(a.getWindow().getDecorView(),"Load · "+savedName)!=null,"Selected allocation saved in device library");down();shot("06_native_local_allocation_library");
        main(()->a.finish());a=(MainActivity)startActivitySync(intent);ready();tab(1);ok(exact(a.getWindow().getDecorView(),"Load · "+savedName)!=null,"Saved allocation survives activity cold restart");main(()->exact(a.getWindow().getDecorView(),"Load · "+savedName).performClick());ready();ok(Math.abs(a.analysis.weights[3]-.6)<1e-12&&a.analysis.name.equals(savedName),"Saved allocation reloads actual weights");
        tab(3);shot("07_native_historical_scenario");main(()->((Spinner)a.findViewById(330)).setSelection(4));ok(a.findViewById(322)!=null,"Native market and rate what-if controls render");main(()->((SeekBar)a.findViewById(322)).setProgress(28));ok(contains(a.getWindow().getDecorView(),"+200 bp"),"Native interest-rate slider updates its assumption");shot("08_native_rate_and_market_what_if");
        tab(4);main(()->{((EditText)a.findViewById(400)).setText("Why REVISE?");a.findViewById(401).performClick();});ok(contains(a.getWindow().getDecorView(),"Human approval is pending"),"Native chat answers selected decision with approval limitation");ok(a.findViewById(410)!=null&&a.findViewById(411)!=null&&a.findViewById(412)!=null,"All three native PDF export controls are present");shot("09_native_guide_chat_and_documents");
        for(String file:new String[]{"technical.pdf","tear_sheet.pdf","ai_usage.pdf"}){try(InputStream in=getTargetContext().getAssets().open(file)){byte[] magic=new byte[4];in.read(magic);ok(new String(magic,"US-ASCII").equals("%PDF"),"Bundled real PDF verified: "+file);}}
        main(()->a.findViewById(410).performClick());boolean saved=false;for(int i=0;i<100&&!saved;i++){AccessibilityNodeInfo node=getUiAutomation().getRootInActiveWindow();if(node!=null){for(AccessibilityNodeInfo item:node.findAccessibilityNodeInfosByText("Save")){String label=item.getText()==null?String.valueOf(item.getContentDescription()):item.getText().toString();String pkg=String.valueOf(item.getPackageName());if(label.equalsIgnoreCase("Save")&&item.isEnabled()&&item.isClickable()&&pkg.contains("documentsui")){saved=item.performAction(AccessibilityNodeInfo.ACTION_CLICK);break;}}}if(!saved)SystemClock.sleep(100);}
        ok(saved,"Android document picker Save action executes");for(int i=0;i<100&&!a.lastExportStatus.startsWith("SAVED:");i++)SystemClock.sleep(100);ok("SAVED:technical.pdf".equals(a.lastExportStatus),"Native PDF export callback completes successfully");
        byte[] exported=bytes(getTargetContext().getContentResolver().openInputStream(Uri.parse(a.lastExportUri)));byte[] bundled=bytes(getTargetContext().getAssets().open("technical.pdf"));ok(Arrays.equals(exported,bundled),"Saved PDF bytes exactly match the bundled technical report");down();shot("10_native_document_export_completed");
        android.content.pm.PackageInfo info=getTargetContext().getPackageManager().getPackageInfo("com.quantumx.aegis",android.content.pm.PackageManager.GET_PERMISSIONS);boolean internet=false;if(info.requestedPermissions!=null)for(String permission:info.requestedPermissions)if(permission.equals("android.permission.INTERNET"))internet=true;ok(!internet,"Installed APK requests no internet permission");
        result.putString("result","PASS");result.putInt("checks",checks.size());result.putString("details",String.join("\n",checks));result.putString("screenshots",shots.getAbsolutePath());finish(Activity.RESULT_OK,result);
    }catch(Throwable e){result.putString("result","FAIL");result.putString("error",e.toString());result.putString("details",String.join("\n",checks));finish(Activity.RESULT_CANCELED,result);}}
}
