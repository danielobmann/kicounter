# -----------------
# Import of packages and data

df = read.csv("data/kicount_old_middleJuly.csv", header=FALSE)
names(df) = c("count", "max", "hour", "minute", "wday", "day", "month")

library(ggplot2)
library(gamlss)
library(dplyr)
library(quantreg)

# -----------------
# Hourly mean per day

df_new = df %>% group_by(wday, hour) %>% summarise(count = mean(count))


ggplot(df_new, aes(x=hour, y=count, col=wday, fill=wday)) + 
  geom_line(alpha=1.3, lwd=2) + 
  xlab("Stunde") + 
  ylab("Anzahl") +
  labs(col="Tag", title="Stündlicher Durchschnitt")


# -----------------
# Assume data is periodic in week and work with this

wdays = unique(df$wday)
df$hourrad = df$hour/23 * 2 * pi
df$daymin = 60*df$hour + df$minute
df$dayminrad = df$daymin/1440 * 2 * pi


model = function(deg=3, day="MO", x="dayminrad", y="count", show=TRUE){
  temp = df[which(df$wday == day), ]
  
  form = as.character("")
  for (i in 1:deg) {
    s = paste("sin(", as.character(i), "*", x, ")", sep = "")
    c = paste("cos(", as.character(i), "*", x, ")", sep = "")
    form = paste(form, s, c, sep=" + ")
  }
  form = paste(y, "~", form)
  q5 = rq(as.formula(form), data=temp, tau=0.05)
  q25 = rq(as.formula(form), data=temp, tau=0.25)
  m = glm(as.formula(form), data=temp, family = poisson(link="log"))
  q75 = rq(as.formula(form), data=temp, tau=0.75)
  q95 = rq(as.formula(form), data=temp, tau=0.95)
  
  # Plot the result
  if (show) {
    p = ggplot(temp, aes(x=get(x))) + 
      geom_point(aes(y=get(y)), col="red") + 
      geom_line(aes(y=m$fitted.values), lwd=2, col="black", alpha=1) +
      geom_ribbon(aes(ymin=q25$fitted.values, ymax=q75$fitted.values), fill="blue", alpha=0.5) +
      geom_ribbon(aes(ymin=q5$fitted.values, ymax=q95$fitted.values), fill="blue", alpha=0.3) +
      xlab("Stunde") + 
      ylab("Anzahl") +
      labs(color="", title=paste("Modell für", day)) + 
      scale_x_continuous(labels=c(0:23), breaks = seq(0, 2*pi, length.out=24))
    print(p)
  }
  
  
  # Set up estimated values for further analysis
  ord = order(temp[, x])
  filter_df = data.frame(time = temp[ord, x], count = m$fitted.values[ord])
  invisible(filter_df)
}

recommend = function(time=3, start=9, end=19, tact=0.5, cond="<= 200", day="MO", deg=3, x="dayminrad", y="count", show=TRUE){
  temp = model(deg=deg, day=day, x=x, y=y)

  Nspots = as.integer((end - start)/tact)
  SPOTS = c()
  
  for (spot in 0:Nspots) {
    startrad = (start + spot*tact)/24 * 2 * pi
    endrad = (start + time + spot*tact)/24 * 2 * pi
    counts = temp[which(temp$time < endrad & temp$time >= startrad), "count"]
    counts = sapply(counts, function(x) paste(x, cond))
    counts = sapply(counts, function(x) eval(str2lang(x)))
    if (all(counts)) {
      SPOTS = c(SPOTS, start + spot*tact)
    }
  }
  if (show) {
    xmin = min(SPOTS)/24*2*pi
    xmax = max(SPOTS)/24*2*pi
    xmaxtime = (max(SPOTS) + time)/24*2*pi
    p = ggplot(temp, aes(x=time, y=count)) + 
      geom_rect(aes(xmin=xmin, xmax=xmax, ymin=0, ymax=Inf), alpha=0.1, col="red", fill="red")+
      geom_rect(aes(xmin=xmax, xmax=xmaxtime, ymin=0, ymax=Inf), col="red", fill="")+
      geom_line(lwd=2)+
      scale_x_continuous(labels=c(0:23), breaks = seq(0, 2*pi, length.out=24)) 
      
    print(p)
  }
  print(SPOTS)
}

recommend(cond="< 200", time=1, end=11)
