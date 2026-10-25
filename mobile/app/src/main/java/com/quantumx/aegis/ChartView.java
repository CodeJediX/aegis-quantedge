package com.quantumx.aegis;
import android.content.Context;
import android.graphics.*;
import android.view.*;
import java.util.Locale;

/** Native canvas chart: drag/tap to inspect observations without a web renderer. */
public final class ChartView extends View {
    private final double[] values,second;private final String unit;private final Paint p=new Paint(3);private int selected=-1;
    public ChartView(Context c,double[] a,double[] b,String u){super(c);values=a;second=b;unit=u;setMinimumHeight(dp(220));setContentDescription("Interactive historical chart. Tap or drag to inspect an observation.");setFocusable(true);}
    private int dp(float x){return (int)(x*getResources().getDisplayMetrics().density+.5f);}
    @Override protected void onDraw(Canvas c){super.onDraw(c);float l=dp(8),r=getWidth()-dp(8),t=dp(36),b=getHeight()-dp(30);double min=Double.POSITIVE_INFINITY,max=Double.NEGATIVE_INFINITY;
        for(double v:values){min=Math.min(min,v);max=Math.max(max,v);}if(second!=null)for(double v:second){min=Math.min(min,v);max=Math.max(max,v);}if(max==min){max+=1;min-=1;}double range=max-min;min-=range*.07;max+=range*.07;
        p.setStrokeWidth(dp(1));p.setColor(Color.rgb(40,64,71));for(int i=0;i<4;i++){float y=t+(b-t)*i/3;c.drawLine(l,y,r,y,p);}drawLine(c,values,l,r,t,b,min,max,Color.rgb(118,223,189));if(second!=null)drawLine(c,second,l,r,t,b,min,max,Color.rgb(230,191,120));
        int i=selected<0?values.length-1:Math.min(selected,values.length-1);String label=unit.equals("USD")?String.format(Locale.US,"Observation %d  /  USD %,.0f",i+1,values[i]):String.format(Locale.US,"Observation %d  /  %.3f×",i+1,values[i]);
        p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(230,241,235));p.setTextSize(dp(12));c.drawText(label,l,dp(18),p);p.setColor(Color.rgb(157,187,186));p.setTextSize(dp(10));c.drawText("EARLIEST",l,getHeight()-dp(9),p);p.setTextAlign(Paint.Align.RIGHT);c.drawText("LATEST",r,getHeight()-dp(9),p);p.setTextAlign(Paint.Align.LEFT);
        if(selected>=0){float x=l+(r-l)*i/Math.max(1,values.length-1);p.setColor(Color.rgb(230,191,120));c.drawLine(x,t,x,b,p);float y=(float)(b-(values[i]-min)/(max-min)*(b-t));c.drawCircle(x,y,dp(4),p);}
    }
    private void drawLine(Canvas c,double[] a,float l,float r,float t,float b,double min,double max,int color){Path path=new Path();for(int i=0;i<a.length;i++){float x=l+(r-l)*i/Math.max(1,a.length-1),y=(float)(b-(a[i]-min)/(max-min)*(b-t));if(i==0)path.moveTo(x,y);else path.lineTo(x,y);}p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(dp(1.7f));c.drawPath(path,p);p.setStyle(Paint.Style.FILL);}
    @Override public boolean onTouchEvent(android.view.MotionEvent e){if(e.getAction()==MotionEvent.ACTION_DOWN||e.getAction()==MotionEvent.ACTION_MOVE){getParent().requestDisallowInterceptTouchEvent(true);selected=Math.max(0,Math.min(values.length-1,(int)((e.getX()-dp(8))/(getWidth()-dp(16))*(values.length-1))));invalidate();return true;}if(e.getAction()==MotionEvent.ACTION_UP){getParent().requestDisallowInterceptTouchEvent(false);performClick();return true;}return super.onTouchEvent(e);}
    @Override public boolean performClick(){super.performClick();return true;}
    @Override public boolean onKeyDown(int key,KeyEvent e){if(key==KeyEvent.KEYCODE_DPAD_RIGHT||key==KeyEvent.KEYCODE_DPAD_LEFT){selected=Math.max(0,Math.min(values.length-1,(selected<0?values.length-1:selected)+(key==KeyEvent.KEYCODE_DPAD_RIGHT?1:-1)));invalidate();return true;}return super.onKeyDown(key,e);}
}
