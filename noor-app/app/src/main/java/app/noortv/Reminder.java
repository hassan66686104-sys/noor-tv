package app.noortv;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;

import java.util.Calendar;

/**
 * Every 45 minutes, a small line in the top corner for 10 seconds: on Friday before maghrib it reminds
 * about Surat Al-Kahf, otherwise it is the salawat line. Only the Kahf shortcut schedules it.
 */
public class Reminder extends BroadcastReceiver {
    static final String SHOW = "app.noortv.SHOW";
    static final long EVERY = 45 * 60 * 1000L;

    static void schedule(Context c) {
        AlarmManager am = c.getSystemService(AlarmManager.class);
        Intent show = new Intent(c, Reminder.class).setAction(SHOW);
        PendingIntent pi = PendingIntent.getBroadcast(c, 0, show,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        am.setInexactRepeating(AlarmManager.ELAPSED_REALTIME, SystemClock.elapsedRealtime() + 60_000, EVERY, pi);
    }

    @Override
    public void onReceive(Context c, Intent i) {
        if (!BuildConfig.REMINDERS) return;
        if (!SHOW.equals(i.getAction())) {
            schedule(c);
            Adhan.schedule(c);
            MessageServer.start(c);
            return;
        }
        if (!Settings.canDrawOverlays(c)) return;
        Calendar now = Calendar.getInstance();
        boolean friday = now.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY && now.get(Calendar.HOUR_OF_DAY) < 17;
        // On Friday the Kahf reminder takes every other turn, so the salawat line still shows.
        android.content.SharedPreferences p = c.getSharedPreferences("reminder", Context.MODE_PRIVATE);
        int n = p.getInt("n", 0);
        p.edit().putInt("n", n + 1).apply();
        boolean kahf = friday && n % 2 == 0;
        show(c.getApplicationContext(), kahf ? "اليوم الجمعة... لا تنسى سورة الكهف" : "صلّ على النبي ﷺ");
    }

    static void show(Context c, String text) {
        WindowManager wm = c.getSystemService(WindowManager.class);
        TextView v = new TextView(c);
        v.setText(text);
        v.setTextColor(Color.WHITE);
        v.setTextSize(22);
        v.setTypeface(Typeface.DEFAULT_BOLD);
        v.setPadding(36, 18, 36, 18);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(0xCC0F3D2E);
        bg.setCornerRadius(40);
        v.setBackground(bg);
        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
                PixelFormat.TRANSLUCENT);
        lp.gravity = Gravity.TOP | Gravity.END;
        lp.x = 48;
        lp.y = 240; // below the launcher's top buttons
        try {
            wm.addView(v, lp);
        } catch (Exception e) {
            return;
        }
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            try {
                wm.removeView(v);
            } catch (Exception ignored) {
            }
        }, 10_000);
    }
}
