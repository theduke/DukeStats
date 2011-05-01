'''
Created on Apr 30, 2011

@author: theduke
'''

import pygooglechart

from pygooglechart import PieChart2D
from pygooglechart import PieChart3D
from pygooglechart import ScatterChart, StackedVerticalBarChart, StackedHorizontalBarChart


class FBStatsVisualizer(object):
    
    def __init__(self):
        self.defaultWidth = 800
        self.defaultHeight = 300        
    
    def buildSexChart(self, data):
        chart = self.buildPieChart3D(data, True)
        chart.set_title('Friends Sex')
        
        return chart
    
    def buildRelatioshipStatusChart(self, data):
        chart = self.buildPieChart2D(data, True)
        chart.set_title('Friends Relationship Status')
        
        return chart
    
    def buildCategorizedAgeChart(self, data):
        chart = self.buildPieChart2D(data, False, True)
        chart.set_title('Friends Age')
        
        return chart
    
    def buildCategorizedPicCountChart(self, data):
        chart = self.buildPieChart2D(data, False, True)
        chart.set_title('Friends Number of Pictures Uploaded')
        
        return chart
    
    def buildCategorizedTagCountChart(self, data):
        chart = self.buildPieChart2D(data, True)
        chart.set_title('Number of Picture Tags')
        
        return chart
    
    def buildAgePhotoCountScatterChart(self, data, xRange, yRange):
        chart = self.buildScatterChart(data, 'count', 'age', xRange, yRange)
        chart.set_title('Age - Number of Pictures')
        chart.set_axis_labels('x', self.buildLabels(xRange))
        chart.set_axis_labels('y', self.buildLabels(yRange))
        
        return chart
    
    def buildAgeTagCountScatterChart(self, data, xRange, yRange):
        chart = self.buildScatterChart(data, 'count', 'age', xRange, yRange)
        chart.set_title('Age - Number of Tags')
        chart.set_axis_labels('x', [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
        chart.set_axis_labels('y', [0, 10, 20, 30, 40, 50, 60, 70, 80])
        
        return chart
    
    def buildMessageSentReceivedScatterChart(self, data):
        chart = self.buildScatterChart(data, 'x', 'y')
        chart.set_title('Messages Sent(X) - Messages Received(Y) per Person')
        
        return chart
    
    def buildTagBuddiesWallPosterScatterChart(self, data):
        chart = ScatterChart(self.defaultWidth, self.defaultHeight)
        
        xData = list()
        yData = list()
        
        for item in data.values():
            xData.append(item[0])
            yData.append(item[1])
        
        chart.add_data(xData)
        chart.add_data(yData)
        
        chart.set_axis_labels('x', self.buildLabels((0, max(xData))))
        chart.set_axis_labels('y', self.buildLabels((0, max(yData))))
        
        chart.set_title('Wall Posts - Common Photo Tags')
        
        return chart
    
    def buildTagBuddiesChart(self, data):
        
        if len(data) > 5:
            data = data[:5]
        
        bars = list()
        labels = list()
        
        for value in data:
            bars.append(value[1])
            labels.append(value[0] + ' (' + str(value[1]) + ')')
        
        chart = PieChart2D(self.defaultWidth, self.defaultHeight)
                
        chart.add_data(bars)
        chart.set_pie_labels(labels)
        
        chart.set_title('TOP 5 Tag Buddies')
        
        return chart
    
    def buildWallPostersChart(self, data):
        
        if len(data) > 5:
            data = data[:5]
        
        values = list()
        keys = list()
        
        for value in data:
            values.append(value[1])
            keys.append(value[0] + ' (' + str(value[1]) + ')')
        
        chart = PieChart2D(self.defaultWidth, self.defaultHeight)
                
        chart.add_data(values)
        chart.set_pie_labels(keys)
        
        chart.set_title('Top 5 People Posting on Your Wall')
        
        return chart
    
    def buildTopRecordsPieChartFromSortedData(self, data, title):
        
        if len(data) > 5:
            data = data[:5]
        
        values = list()
        keys = list()
        
        for value in data:
            values.append(value[1])
            keys.append(self.removeNonAscii(value[0]) + ' (' + str(value[1]) + ')')
        
        chart = PieChart2D(self.defaultWidth, self.defaultHeight)
                
        chart.add_data(values)
        chart.set_pie_labels(keys)
        
        chart.set_title(title)
        
        return chart
    
    def buildLabels(self, theRange, labelCount=10):
        labels = list()
        labels.append(theRange[0])
         
        valRange = theRange[1] - theRange[0]
        
        if valRange < labelCount:
            labelCount = valRange
        
        step = valRange / labelCount
        
        for i in range(labelCount):
            labels.append(labels[len(labels) - 1] + step)
            
        return labels
    
    
    def buildScatterChart(self, data, xKey, yKey, x_range=None, y_range=None, buildLabels=False):
        chart = ScatterChart(self.defaultWidth, self.defaultHeight)
        
        xData = list()
        yData = list()
        
        for item in data:
            xData.append(item[xKey])
            yData.append(item[yKey])
            
        chart.add_data(xData)
        chart.add_data(yData)
        
        if not x_range: x_range = (0, max(xData))
        if not y_range: y_range = (0, max(yData))
        
        chart.set_axis_range('x', x_range[0], x_range[1])
        chart.set_axis_range('y', y_range[0], y_range[1])
            
        if buildLabels:
            chart.set_axis_labels('x', self.buildLabels(x_range))
            chart.set_axis_labels('y', self.buildLabels(y_range))
        
        return chart
        
    def buildPieChart3D(self, data, addValueToLabel=False, sortByKeys=False):
        chart = PieChart3D(self.defaultWidth, self.defaultHeight)
        
        labels = list()
        dataPoints = list()
        
        keys = sorted(data.keys()) if sortByKeys else data.keys()
        for key in keys:
            value = data[key]
            label = key
            
            if addValueToLabel: label += ' (' + str(value) + ')'
            
            labels.append(label)
            dataPoints.append(value)
                
            
        chart.add_data(dataPoints)
        chart.set_pie_labels(labels)
        
        return chart      
    
    
    def buildPieChart2D(self, data, addValueToLabel=False, sortByKeys=False):
        chart = PieChart2D(self.defaultWidth, self.defaultHeight)
        
        labels = list()
        dataPoints = list()
        
        keys = sorted(data.keys()) if sortByKeys else data.keys()
        for key in keys:
            value = data[key]
            label = key
            
            if addValueToLabel: label += ' (' + str(value) + ')'
            
            labels.append(label)
            dataPoints.append(value)
                
            
        chart.add_data(dataPoints)
        chart.set_pie_labels(labels)
        
        return chart     
    
    def removeNonAscii(self, s): return "".join(i for i in s if ord(i)<128)   
            