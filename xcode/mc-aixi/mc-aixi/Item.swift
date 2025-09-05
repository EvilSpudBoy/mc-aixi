//
//  Item.swift
//  mc-aixi
//
//  Created by Michael Stevens on 9/5/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
