var segmentIndex = -1;
var tagDefinitions = [];
var segments = [];

var tokens = [];
var startIndex = -1;
var endIndex = -1;
var selecting = false;
var wordSpans = [];
var tagged = [];

var allowOverlap = false;

var undoManager = new UndoManager();

function init() {
	$("#previous").button().click(previousSegment);
	$("#next").button().click(nextSegment);
	$("#retransmit").button().click(retransmit);
	$("#undo").button().click(function() {
		undoManager.undo();
	});
	$("#segmentList").dblclick(function() {
		openSegment($("#segmentList").prop("selectedIndex"));
	});
	$("#openSegment").button().click(function() {
		openSegment($("#segmentList").prop("selectedIndex"));
	});

	console.log("Retrieving tag definitions...");
	$.ajax(
		"/",
		{ data: { action: "get_tag_definitions" } }
	).done(function(newTagDefinitions) {
		tagDefinitions = newTagDefinitions;
		
		$.ajax(
			"/",
			{ data: { action: "get_segments" } }
		).done(function(newSegments) {
			segments = newSegments;
			updateSegments();
			if (segments.length == 0) {
				alert("Error: No segments received!");
				return;
			}
			openSegment(0);
		}).error(function(jqxhr, textStatus, errorThrown) {
			alert(errorThrown);
		});
	}).error(function(jqxhr, textStatus, errorThrown) {
		alert(errorThrown);
	});
	
	$(document).keypress(function(event) {
		if (event.key == "ArrowLeft") {
			previousSegment();
		} else if (event.key == "ArrowRight") {
			nextSegment();
		} else if (event.key == 'z' && event.ctrlKey) {
			undoManager.undo();
		} else if (event.key >= '0' && event.key <= '9') {
			setTag(parseInt(event.key) - 1);
		}
	});
}

function openSegment(newSegmentIndex) {
	var oldSegmentIndex = segmentIndex;
	segmentIndex = newSegmentIndex;
	loadSegment();
	
	if (oldSegmentIndex !== undefined && oldSegmentIndex >= 0) {
		undoManager.add({
			undo: function() {
				segmentIndex = oldSegmentIndex;
				loadSegment();
			}
		});
	}
}

function loadSegment() {
	var segment = segments[segmentIndex];
	
	console.log("Retrieving tokens for segment »" + segment + "«...");
	$.ajax(
		"/",
		{ data: { action: "get_tokens", segment: segment } }
	).done(function(newTokens) {
		tokens = newTokens;
		startIndex = -1;
		endIndex = -1;
		selecting = false;
		wordSpans = [];
		tagged = [];
		
		createText("#document", tokens);
		createTagList("#tags", tagDefinitions);
		
		console.log("Retrieving tags...");
		
		$.ajax(
			"/",
			{ data: { action: "get_tags", segment: segment } }
		).done(function(newTags) {
			for (var i = 0; i < newTags.length; i++) {
				var tag = newTags[i][0];
				var start = newTags[i][1];
				var end = newTags[i][2];
				addTagDecoration(tag, start, end);
			}
			
			$("#title").text(segment);
		}).error(function(jqxhr, textStatus, errorThrown) {
			alert(errorThrown);
		});
	}).error(function(jqxhr, textStatus, errorThrown) {
		alert(errorThrown);
	});
}

function updateSegments() {
	for (var i = 0; i < segments.length; i++) {
		$("#segmentList").append($('<option></option>').attr("value", segments[i]).text(segments[i]));
	}
}

function updateSelection(spans, startIndex, endIndex) {
	if (startIndex > endIndex) {
		var tmp = startIndex;
		startIndex = endIndex;
		endIndex = tmp;
	}
	
	for (var i = 0; i < spans.length; i++) {
		if (i == startIndex && i == endIndex) {
			spans[i].removeClass("SelectedLeft");
			spans[i].removeClass("SelectedMiddle");
			spans[i].removeClass("SelectedRight");
			spans[i].addClass("SelectedSingle");
		} else {
			spans[i].removeClass("SelectedSingle");
			
			if (i == startIndex) {
				spans[i].addClass("SelectedLeft");
				spans[i].removeClass("SelectedMiddle");
				spans[i].removeClass("SelectedRight");
			} else if (i == endIndex) {
				spans[i].removeClass("SelectedLeft");
				spans[i].removeClass("SelectedMiddle");
				spans[i].addClass("SelectedRight");
			} else if (i >= startIndex && i <= endIndex) {
				spans[i].removeClass("SelectedLeft");
				spans[i].addClass("SelectedMiddle");
				spans[i].removeClass("SelectedRight");
			} else {
				spans[i].removeClass("SelectedLeft");
				spans[i].removeClass("SelectedMiddle");
				spans[i].removeClass("SelectedRight");
			}
		}
		
	}
}

function createText(container, tokens) {
	$(container).empty();
	
	function mouseDown(index) {
		return function() {
			startIndex = index;
			endIndex = index;
			selecting = true;
			updateSelection(wordSpans, startIndex, endIndex);
		};
	}
	
	function mouseEnter(index) {
		return function() {
			if (!selecting) {
				return;
			}
			endIndex = index;
			updateSelection(wordSpans, startIndex, endIndex);
		};
	}
	
	for (var i = 0; i < tokens.length; i++) {
		var span = $("<span></span>").addClass("AnnotationText").text(tokens[i]);
		span.mousedown(mouseDown(i));
		span.mouseenter(mouseEnter(i));
		$(container).append(span);
		wordSpans.push(span);
	}
	
	$(document).mouseup(function() {
		selecting = false;
		updateSelection(wordSpans, startIndex, endIndex);
	});
	
	
	$(container).mousedown(function(event) {
		if (selecting || event.target != this) {
			return;
		}
		startIndex = -1;
		endIndex = -1;
		updateSelection(wordSpans, startIndex, endIndex);
	});
}

function setTag(tag) {
	if (startIndex < 0 || endIndex < 0) {
		return;
	}
	
	if (startIndex > endIndex) {
		var tmp = startIndex;
		startIndex = endIndex;
		endIndex = tmp;
	}
	
	if (tag < 0) {
		removeTags(startIndex, endIndex);
	} else if (tag < tagDefinitions.length) {
		if (tagExists(tag, startIndex, endIndex)) {
			removeTag(tag, startIndex, endIndex);
		} else {
			addTag(tag, startIndex, endIndex);
		}
	}
}

function addTagDecoration(tag, startIndex, endIndex) {
	for (var i = 0; i < tagged.length; i++) {
		if (
			tagged[i][0] == tag &&
			tagged[i][1] == startIndex &&
			tagged[i][2] == endIndex
		) {
			return;
		}
	}
	
	tagged.push([tag, startIndex, endIndex]);
	updateTags();
}

function tagExists(tag, startIndex, endIndex) {
	for (var i = 0; i < tagged.length; i++) {
		if (
			tagged[i][0] == tag &&
			tagged[i][1] == startIndex &&
			tagged[i][2] == endIndex
		) {
			return true;
		}
	}
	
	return false;
}

function addTag(tag, startIndex, endIndex) {
	if (!allowOverlap) {
		for (var i = 0; i < tagged.length; i++) {
			var t = tagged[i];
			if (
				t[0] == tag &&
				t[1] <= endIndex &&
				startIndex <= t[2]
			) {
				alert("Overlapping annotations are disabled!");
				return;
			}
		}
	}
	
	doAddTag(tag, startIndex, endIndex);
	undoManager.add({
		undo: function() {
			doRemoveTag(tag, startIndex, endIndex);
		}
	});
}

function doAddTag(tag, startIndex, endIndex) {
	addTagDecoration(tag, startIndex, endIndex);
	
	$("#document").css("background-image", 'url("wait.gif")');
	$.ajax(
		"/",
		{ data: { action: "set_tag", segment: segments[segmentIndex], tag: tag, start: startIndex, end: endIndex } }
	).done(function() {
		$("#document").css("background-image", "none");
	}).error(function(jqxhr, textStatus, errorThrown) {
		$("#document").css("background-image", "none");
		alert(textStatus + "\n" + errorThrown);
	});
}

function removeTag(tag, startIndex, endIndex) {
	doRemoveTag(tag, startIndex, endIndex);
	undoManager.add({
		undo: function() {
			doAddTag(tag, startIndex, endIndex);
		}
	});
}

function doRemoveTag(tag, startIndex, endIndex) {
	tagged = tagged.filter(function(t) {
		return !(t[0] == tag && t[1] == startIndex && t[2] == endIndex);
	});
	
	updateTags();
	
	$("#document").css("background-image", 'url("wait.gif")');
	$.ajax(
		"/",
		{ data: { action: "remove_tag", segment: segments[segmentIndex], tag: tag, start: startIndex, end: endIndex } }
	).done(function() {
		$("#document").css("background-image", "none");
	}).error(function(jqxhr, textStatus, errorThrown) {
		$("#document").css("background-image", "none");
		alert(textStatus + "\n" + errorThrown);
	});
}

function removeTags(startIndex, endIndex) {
	var removed = [];
	tagged = tagged.filter(function(t) {
		if (t[1] <= endIndex && startIndex <= t[2]) {
			removed.push(t);
			return false;
		} else {
			return true;
		}
	});
	
	if (removed.length > 0) {
		undoManager.add({
			undo: function() {
				for (var i = 0; i < removed.length; i++) {
					var t = removed[i];
					doAddTag(t[0], t[1], t[2]);
				}
			}
		});
		
		$("#document").css("background-image", 'url("wait.gif")');
		function submit(index) {
			$.ajax(
				"/",
				{ data: { action: "remove_tag", segment: segments[segmentIndex], tag: removed[index][0], start: removed[index][1], end: removed[index][2] } }
			).done(function() {
				index++;
				if (index >= removed.length) {
					$("#document").css("background-image", "none");
				} else {
					submit(index);
				}
			}).error(function(jqxhr, textStatus, errorThrown) {
				$("#document").css("background-image", "none");
				alert(textStatus + "\n" + errorThrown);
			});
		}
		
		submit(0);
	}
	
	updateTags();
}

function updateTags() {
	tagged.sort(function(a, b) {
		return a[1] - b[1];
	});
	
	
	var startsHere = [];
	var endsHere = [];
	var isHere = [];
	for (var i = 0; i < tagged.length; i++) {
		var tag = tagged[i][0];
		var start = tagged[i][1];
		var end = tagged[i][2];
		
		if (startsHere[start] === undefined) {
			startsHere[start] = [ tag ];
		} else if (startsHere[start].indexOf(tag) < 0) {
			startsHere[start].push(tag);
		}
		
		if (endsHere[end] === undefined) {
			endsHere[end] = [ tag ];
		} else if (endsHere[end].indexOf(tag) < 0) {
			endsHere[end].push(tag);
		}
		
		for (var j = start; j <= end; j++) {
			if (isHere[j] === undefined) {
				isHere[j] = [ tag ];
			} else if (isHere[j].indexOf(tag) < 0) {
				isHere[j].push(tag);
			}
		}
	}
	
	function tagGradient(tagIndices) {
		if (tagIndices.length == 1) {
			return tagDefinitions[tagIndices[0]][1] + ", " + tagDefinitions[tagIndices[0]][1];
		}
		
		var gradient = "";
		for (var i = 0; i < tagIndices.length; i++) {
			if (i != 0) {
				gradient += ", ";
			}
			gradient += tagDefinitions[tagIndices[i]][1];
		}
		
		return gradient;
	}
	
	for (var i = 0; i < wordSpans.length; i++) {
		if (isHere[i] === undefined || isHere[i].length == 0) {
			wordSpans[i].removeClass("Tagged");
			wordSpans[i].css("background-image", "none");
			continue;
		}
		
		wordSpans[i].addClass("Tagged");
		
		isHere[i].sort();
		var gradient = "linear-gradient(to right, " + tagGradient(isHere[i]) + ")";
		
		if (startsHere[i] !== undefined) {
			startsHere[i].sort();
			gradient += ", linear-gradient(to top, " + tagGradient(startsHere[i]) + ")";
		} else {
			gradient += ", linear-gradient(to top, transparent, transparent)";
		}
		
		if (endsHere[i] !== undefined) {
			endsHere[i].sort();
			gradient += ", linear-gradient(to bottom, " + tagGradient(endsHere[i]) + ")";
		} else {
			gradient += ", linear-gradient(to bottom, transparent, transparent)";
		}
		
		wordSpans[i].css("background-image", gradient);
	}
	
	// Log
	var container = "#tagLog";
	$(container).empty();
	
	for (var i = 0; i < tagged.length; i++) {
		var tag = tagged[i][0];
		var start = tagged[i][1];
		var end = tagged[i][2];
		
		var div = $("<div></div>");
		div.text("[" + start + "→" + end + "] " + tagDefinitions[tag][0] + " »" + tokens.slice(start, end+1) + "«");
		div.appendTo(container);
	}
}

function createTagList(container, tags) {
	$(container).empty();
	var list = $("<ol></ol>");
	list.appendTo($(container));
	
	function setTagFunction(tag) {
		return function() {
			setTag(tag);
		};
	}
	
	var a = $('<a title="Press 0 to remove all tags from the selection."></a>').text("Clear selected");
	a.click(setTagFunction(-1));
	a.css("border-bottom", "2px dotted gray");
	var li = $('<li value="0"></li>');
	a.appendTo(li);
	li.appendTo(list);
	
	for (var i = 0; i < tags.length; i++) {
		var a = $('<a title="Press ' + (i+1) + ' to add this tag to the selection."></a>').text(tags[i][0]);
		a.click(setTagFunction(i));
		a.css("border-bottom", "2px solid " + tags[i][1]);
		var li = $("<li></li>");
		a.appendTo(li);
		li.appendTo(list);
	}
}

function previousSegment() {
	if (segmentIndex <= 0) {
		alert("Already at first segment!");
		return;
	}
	
	openSegment(segmentIndex-1);
}

function nextSegment() {
	if (segmentIndex >= segments.length-1) {
		alert("Already at last segment!");
		return;
	}
	
	openSegment(segmentIndex+1);
}

function retransmit() {
	$("#document").css("background-image", 'url("wait.gif")');
	
	function submit(index) {
		$.ajax(
			"/",
			{ data: { action: "set_tag", segment: segments[segmentIndex], tag: tagged[index][0], start: tagged[index][1], end: tagged[index][2] } }
		).done(function() {
			index++;
			if (index >= tagged.length) {
				$("#document").css("background-image", "none");
			} else {
				submit(index);
			}
		}).error(function(jqxhr, textStatus, errorThrown) {
			$("#document").css("background-image", "none");
			alert(textStatus + "\n" + errorThrown);
		});
	}
	
	$.ajax(
		"/",
		{ data: { action: "clear_tags", segment: segments[segmentIndex] } }
	).done(function() {
		submit(0);
	}).error(function(jqxhr, textStatus, errorThrown) {
		$("#document").css("background-image", "none");
		alert(textStatus + "\n" + errorThrown);
	});
}
