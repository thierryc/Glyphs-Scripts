#MenuTitle: Compound Variabler
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Reduplicates Brace and Bracket layers of components in the compounds in which they are used. Makes brace and bracket layers work in the compounds.
"""

import vanilla

class CompoundVariabler( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 410
		windowHeight = 215
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Compound Variabler", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CompoundVariabler.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 28), u"Reduplicates Brace and Bracket layers of components in the compounds in which they are used. Makes brace and bracket layers work in the compounds.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.allGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include all exporting glyphs in font (otherwise only selected glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.allGlyphs.getNSButton().setToolTip_("If checked, all glyphs in the font will be processed and receive the special (brace and bracket) layers of their respective components. If unchecked, only selected compound glyphs get processed.")
		linePos += lineHeight
		
		self.w.deleteExistingSpecialLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Delete pre-existing special layers in compounds", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.deleteExistingSpecialLayers.getNSButton().setToolTip_("If checked, will delete all brace and bracket layers found in processed compound glyphs.")
		linePos += lineHeight
		
		self.w.openTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Open tab with affected compounds", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTab.getNSButton().setToolTip_("If checked, will open a tab with all compounds that have received new special layers.")
		linePos += lineHeight
		
		self.w.catchNestedComponents = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Catch all nested components (slower)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.catchNestedComponents.getNSButton().setToolTip_(u"If checked, will count max component depth (number of nestings, i.e. components of components of components, etc.) in the font, and repeat the whole process as many times. Will take significantly longer.")
		linePos += lineHeight
		
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		self.w.processedGlyph = vanilla.TextBox( (inset, linePos+2, -80-inset, 14), u"", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Run", sizeStyle='regular', callback=self.CompoundVariablerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Compound Variabler' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CompoundVariabler.allGlyphs"] = self.w.allGlyphs.get()
			Glyphs.defaults["com.mekkablue.CompoundVariabler.openTab"] = self.w.openTab.get()
			Glyphs.defaults["com.mekkablue.CompoundVariabler.deleteExistingSpecialLayers"] = self.w.deleteExistingSpecialLayers.get()
			Glyphs.defaults["com.mekkablue.CompoundVariabler.catchNestedComponents"] = self.w.catchNestedComponents.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.CompoundVariabler.allGlyphs", 1)
			Glyphs.registerDefault("com.mekkablue.CompoundVariabler.openTab", 0)
			Glyphs.registerDefault("com.mekkablue.CompoundVariabler.deleteExistingSpecialLayers", 0)
			Glyphs.registerDefault("com.mekkablue.CompoundVariabler.catchNestedComponents", 0)
			self.w.allGlyphs.set( Glyphs.defaults["com.mekkablue.CompoundVariabler.allGlyphs"] )
			self.w.openTab.set( Glyphs.defaults["com.mekkablue.CompoundVariabler.openTab"] )
			self.w.deleteExistingSpecialLayers.set( Glyphs.defaults["com.mekkablue.CompoundVariabler.deleteExistingSpecialLayers"] )
			self.w.catchNestedComponents.set( Glyphs.defaults["com.mekkablue.CompoundVariabler.catchNestedComponents"] )
		except:
			return False
			
		return True
	
	def countNest(self, c):
		thisFont = c.parent.parent
		if thisFont:
			gName = c.componentName
			g = thisFont.glyphs[gName]
			if g:
				gComponents = g.layers[0].components
				if gComponents:
					maxCount = max( countNest(cc) for cc in gComponents )
					return 1+maxCount
		return 1
		
	def depthOfNesting(self, thisFont):
		depths=[]
		for g in Font.glyphs:
			for l in g.layers:
				if l.isMasterLayer or l.isSpecialLayer or l.isColorLayer:
					for c in l.components:
						depth = countNest(c)
						depths.append(depth)
		return max(depths)

	def CompoundVariablerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Compound Variabler' could not write preferences.")
			
			allGlyphs = Glyphs.defaults["com.mekkablue.CompoundVariabler.allGlyphs"]
			openTab = Glyphs.defaults["com.mekkablue.CompoundVariabler.openTab"]
			deleteExistingSpecialLayers = Glyphs.defaults["com.mekkablue.CompoundVariabler.deleteExistingSpecialLayers"]
			catchNestedComponents = Glyphs.defaults["com.mekkablue.CompoundVariabler.catchNestedComponents"]
			
			thisFont = Glyphs.font # frontmost font
			print("Compound Variabler Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			depth = 1
			if catchNestedComponents:
				print("Catching all component nestings...")
				depth = self.depthOfNesting(thisFont)
				depth = max(1,depth) # minimum 1, just to make sure
				print(
					"Found components nested up to %i time%s" % (
						depth,
						"" if depth==1 else "s",
					)
				)
			
			if allGlyphs:
				glyphs = [g for g in thisFont.glyphs if g.export]
				print("Processing all glyphs (%i in total)..." % len(glyphs))
			else:
				glyphs = [l.parent for l in thisFont.selectedLayers if l.parent.export]
				print("Processing selected glyphs (%i in total)..." % len(glyphs))
			
			for depthIteration in range(depth):
				depthStatusAddition=""
				if depth>1:
					print("\nNesting iteration %i:"%(depthIteration+1))
					depthStatusAddition="%i: "%(depthIteration+1)
					
				glyphCount = len(glyphs)
				affectedGlyphs = []
				for i,currentGlyph in enumerate(glyphs):
					# status update
					self.w.progress.set(i*100.0/glyphCount)
					processMessage = "%s%s" % (depthStatusAddition, currentGlyph.name)
					self.w.processedGlyph.set( processMessage )
					# print processMessage
				
					# process layers
					thisLayer = currentGlyph.layers[0]
					if thisLayer.components:
				
						# delete special layers if requested:
						if deleteExistingSpecialLayers:
							layerCount = len(currentGlyph.layers)
							for i in reversed(range(layerCount)):
								if currentGlyph.layers[i].isSpecialLayer:
									print("%s: deleted layer '%s'" % (currentGlyph.name, currentGlyph.layers[i].name))
									del currentGlyph.layers[i]
				
						for component in thisLayer.components:
							originalGlyph = thisFont.glyphs[component.componentName]
							if originalGlyph:
								for originalLayer in originalGlyph.layers:
									if originalLayer.isSpecialLayer:
										namesAndMasterIDsOfSpecialLayers = [(l.name,l.associatedMasterId) for l in currentGlyph.layers if l.isSpecialLayer]
										layerAlreadyExists = False
										for currentGlyphLayer in currentGlyph.layers:
											nameIsTheSame = originalLayer.name == currentGlyphLayer.name
											masterIsTheSame = originalLayer.associatedMasterId == currentGlyphLayer.associatedMasterId
											if nameIsTheSame and masterIsTheSame:
												layerAlreadyExists = True
										if layerAlreadyExists:
											print("%s, layer '%s' already exists. Skipping." % (currentGlyph.name, originalLayer.name))
										else:
											newLayer = GSLayer()
											newLayer.name = originalLayer.name
											newLayer.setAssociatedMasterId_(originalLayer.associatedMasterId)
											currentGlyph.layers.append(newLayer)
											newLayer.reinterpolate()
											affectedGlyphs.append(currentGlyph.name)
											print("%s, new layer: '%s'" % (currentGlyph.name, newLayer.name))

			# status update
			self.w.progress.set(100)
			self.w.processedGlyph.set( "Done." )
			print("Done.")
			
			if affectedGlyphs:
				if openTab:
					# opens new Edit tab:
					tabText = "/" + "/".join(set(affectedGlyphs))
					thisFont.newTab( tabText )

				# Floating notification:
				numOfGlyphs = len(set(affectedGlyphs))
				Glyphs.showNotification( 
					u"%s" % (thisFont.familyName),
					u"Compound Variabler added layers to %i compound glyph%s." % (
							numOfGlyphs,
							"" if numOfGlyphs==1 else "s",
						),
					)
				
			else:
				# Floating notification:
				Glyphs.showNotification( 
					u"%s" % (thisFont.familyName),
					u"Compound Variabler added no new layers.",
					)
					
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compound Variabler Error: %s" % e)
			import traceback
			print(traceback.format_exc())

CompoundVariabler()